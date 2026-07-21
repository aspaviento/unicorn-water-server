export const content = {
  appName: 'Unicorn Water Server',
  navigation: {
    ariaLabel: 'Main navigation',
    home: 'Panel',
    apiDocs: 'API docs',
  },
  panel: {
    waterAriaLabel: (liters: number) => `Daily water consumption: ${liters} litres`,
    statusSummary: (activeRows: number, displayMode: string, overflow: boolean) =>
      `${activeRows} of 5 bucket rows · ${displayMode} display${overflow ? ' · 999+ overflow' : ''}`,
    poolSummary: (phStatus: string | null, phValue: number | null, orpStatus: string | null, orpValue: number | null) => {
      const ph = phStatus ? `pH ${phStatus}${phValue === null ? '' : ` (${phValue})`}` : 'pH not set';
      const orp = orpStatus ? `ORP ${orpStatus}${orpValue === null ? '' : ` (${orpValue} mV)`}` : 'ORP not set';
      return `${ph} · ${orp}`;
    },
    waterSection: 'Daily water consumption',
    litersLabel: (liters: number) => `Litres: ${liters}`,
    litersInputLabel: 'Consumed litres',
    waterSubmit: 'Update water',
    displaySection: 'Display controls',
    rainbow: 'Rainbow',
    standby: 'Standby',
    off: 'Off',
    apiError: (message: string) => `API error: ${message}`,
  },
  docs: {
    title: 'Server API',
    description: 'HTTP endpoints available to update and inspect the water consumption display.',
    methodLabel: 'Method',
    endpointLabel: 'Endpoint',
    requestLabel: 'Request body',
    descriptionLabel: 'Description',
    endpoints: [
      {
        methods: ['GET'],
        endpoint: '/api/',
        request: 'None',
        description: 'Returns the available Water Server API endpoints.',
      },
      {
        methods: ['POST'],
        endpoint: '/api/water',
        request: '{"liters": 30}',
        description: 'Updates daily consumed litres. Values above 999 are accepted and displayed as red 999 overflow.',
      },
      {
        methods: ['POST'],
        endpoint: '/api/pool',
        request: '{"ph":{"status":"warning","value":6.9},"orp":{"status":"ok","value":697}}',
        description: 'Updates pool chemistry indicators. pH uses the lower-left pixel and ORP uses the next pixel. Status accepts ok, warning, critical, or null.',
      },
      {
        methods: ['GET'],
        endpoint: '/api/status',
        request: 'None',
        description: 'Returns litres, displayed litres, overflow state, pool indicators, active bucket rows, display dimensions, rotation, hardware type, and last update information.',
      },
      {
        methods: ['POST'],
        endpoint: '/api/rainbow',
        request: '{"brightness": 1, "speed": 0.1}',
        description: 'Starts the hardware validation rainbow. Brightness and speed are optional.',
      },
      {
        methods: ['GET', 'POST'],
        endpoint: '/api/standby',
        request: 'None',
        description: 'Shows a very dim standby clock. Repeated calls keep the existing standby display running.',
      },
      {
        methods: ['GET', 'POST'],
        endpoint: '/api/off',
        request: 'None',
        description: 'Stops any animation and turns off every display pixel.',
      },
    ],
  },
};
