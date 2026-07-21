# Home Assistant Integration

Home Assistant can monitor Unicorn Water Server with its built-in REST
integration. The sensor polls `GET /api/status`; when the HTTP endpoint is
reachable the entity state is `running`, and the API response is exposed as
sensor attributes.

The examples below intentionally use placeholder host names. Replace
`<water-server-host>` with the hostname or IP address of the Raspberry Pi that
runs `unicorn-water.service`.

## Enable Packages

If your Home Assistant configuration does not already load packages, add this
under `homeassistant:` in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Then create `packages/unicorn_water_server.yaml`:

```yaml
rest:
  - resource: http://<water-server-host>:9002/api/status
    scan_interval: 60
    timeout: 5
    sensor:
      - name: Unicorn Water Server
        unique_id: unicorn_water_server_status
        value_template: "running"
        json_attributes:
          - activeRows
          - displayLiters
          - displayMode
          - height
          - lastCalled
          - lastCalledApi
          - liters
          - overflow
          - pool
          - rotation
          - unicorn
          - width
```

Validate and restart Home Assistant after adding the package. The sensor entity
will be `sensor.unicorn_water_server`.

`displayMode` can be `water`, `rainbow`, `standby`, or `off`. Standby is the
intentional quiet display mode and shows a dim `HH:MM` clock on the physical
matrix.

## Dashboard Card

The visual matrix example uses
[`button-card`](https://github.com/custom-cards/button-card). Install it through
HACS or add it as a Lovelace resource before using `custom:button-card`.

```yaml
type: vertical-stack
cards:
  - type: conditional
    conditions:
      - entity: sensor.unicorn_water_server
        state: running
    card:
      type: custom:button-card
      entity: sensor.unicorn_water_server
      name: Unicorn Water Server
      show_state: false
      show_icon: false
      styles:
        card:
          - padding: 16px
        name:
          - font-size: 18px
          - justify-self: start
          - margin-bottom: 12px
        custom_fields:
          matrix:
            - display: grid
            - grid-template-columns: repeat(17, 10px)
            - grid-template-rows: repeat(7, 10px)
            - gap: 3px
            - background: "#10141c"
            - padding: 10px
            - border-radius: 6px
            - width: max-content
      custom_fields:
        matrix: |
          [[[
            const attrs = entity.attributes;
            const displayMode = attrs.displayMode ?? "water";
            const liters = Number(attrs.displayLiters ?? attrs.liters ?? 0);
            const overflow = attrs.overflow === true;
            const activeRows = Math.max(0, Math.min(5, Number(attrs.activeRows ?? 0)));
            const pool = attrs.pool ?? {};

            const colors = {
              off: "#202837",
              outline: "#beeaff",
              text: "#34b2ff",
              overflow: "#ff2d40",
              lowBlue: "#004891",
              midBlue: "#0084dc",
              highBlue: "#26baff",
              foam: "#b6f4ff",
              standby: "#80beff",
              ok: "#2666ff",
              warning: "#ffbf00",
              critical: "#ff2d40"
            };

            const digits = {
              "0": ["111", "101", "101", "101", "111"],
              "1": ["010", "110", "010", "010", "111"],
              "2": ["111", "001", "111", "100", "111"],
              "3": ["111", "001", "111", "001", "111"],
              "4": ["101", "101", "111", "001", "001"],
              "5": ["111", "100", "111", "001", "111"],
              "6": ["111", "100", "111", "101", "111"],
              "7": ["111", "001", "010", "010", "010"],
              "8": ["111", "101", "111", "101", "111"],
              "9": ["111", "101", "111", "001", "111"]
            };

            const grid = Array.from({ length: 7 }, () => Array(17).fill(colors.off));

            function setPixel(x, y, color) {
              if (x >= 0 && x < 17 && y >= 0 && y < 7) grid[y][x] = color;
            }

            function drawDigit(digit, xOffset, color) {
              const pattern = digits[digit];
              for (let y = 0; y < 5; y++) {
                for (let x = 0; x < 3; x++) {
                  if (pattern[y][x] === "1") setPixel(xOffset + x, y + 1, color);
                }
              }
            }

            function renderGrid() {
              return grid.flatMap(row =>
                row.map(color => `<span style="
                  width:10px;
                  height:10px;
                  border-radius:50%;
                  background:${color};
                  box-shadow:${color === colors.off ? "none" : `0 0 5px ${color}`};
                  display:block;
                "></span>`)
              ).join("");
            }

            if (displayMode === "standby") {
              const now = new Date();
              const clock = `${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}`;
              drawDigit(clock[0], 0, colors.standby);
              drawDigit(clock[1], 4, colors.standby);
              setPixel(8, 2, colors.standby);
              setPixel(8, 4, colors.standby);
              drawDigit(clock[2], 10, colors.standby);
              drawDigit(clock[3], 14, colors.standby);
              return renderGrid();
            }

            const value = String(Math.trunc(liters)).padStart(3, " ").slice(-3);
            const textColor = overflow ? colors.overflow : colors.text;

            for (let digitIndex = 0; digitIndex < value.length; digitIndex++) {
              const digit = value[digitIndex];
              if (digit === " ") continue;

              drawDigit(digit, digitIndex * 4, textColor);
            }

            const bucketLeft = 12;
            const bucketRight = 16;
            const innerLeft = 13;
            const innerRight = 15;

            for (let x = bucketLeft; x <= bucketRight; x++) setPixel(x, 6, colors.outline);
            for (let y = 1; y <= 6; y++) {
              setPixel(bucketLeft, y, colors.outline);
              setPixel(bucketRight, y, colors.outline);
            }

            if (activeRows > 0) {
              const filledRows = [];
              for (let y = 5; y >= 5 - activeRows + 1; y--) filledRows.push(y);
              const surfaceY = Math.min(...filledRows);

              for (let x = innerLeft; x <= innerRight; x++) {
                for (const y of filledRows) {
                  let color;
                  if (y === surfaceY) {
                    color = x === innerLeft ? colors.foam : colors.highBlue;
                  } else if (y >= 4) {
                    color = colors.lowBlue;
                  } else {
                    color = colors.midBlue;
                  }
                  setPixel(x, y, color);
                }
              }
            }

            const phStatus = pool.ph?.status;
            const orpStatus = pool.orp?.status;

            if (colors[phStatus]) setPixel(0, 6, colors[phStatus]);
            if (colors[orpStatus]) setPixel(1, 6, colors[orpStatus]);

            return renderGrid();
          ]]]

  - type: entities
    show_header_toggle: false
    entities:
      - entity: sensor.unicorn_water_server
        name: Status

      - type: attribute
        entity: sensor.unicorn_water_server
        attribute: liters
        name: Liters
        suffix: " L"

      - type: attribute
        entity: sensor.unicorn_water_server
        attribute: displayLiters
        name: Display Liters
        suffix: " L"

      - type: attribute
        entity: sensor.unicorn_water_server
        attribute: activeRows
        name: Active Rows

      - type: attribute
        entity: sensor.unicorn_water_server
        attribute: overflow
        name: Overflow

      - type: attribute
        entity: sensor.unicorn_water_server
        attribute: displayMode
        name: Display Mode

      - type: attribute
        entity: sensor.unicorn_water_server
        attribute: lastCalled
        name: Last Called

      - type: attribute
        entity: sensor.unicorn_water_server
        attribute: lastCalledApi
        name: Last Called API

  - type: markdown
    content: |
      **Pool**

      **pH:** {{ state_attr('sensor.unicorn_water_server', 'pool').ph.value }}
      ({{ state_attr('sensor.unicorn_water_server', 'pool').ph.status }})

      **ORP:** {{ state_attr('sensor.unicorn_water_server', 'pool').orp.value }}
      ({{ state_attr('sensor.unicorn_water_server', 'pool').orp.status }})
```
