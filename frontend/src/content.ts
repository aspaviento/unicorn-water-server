export const content = {
  appName: 'Unicorn Water Server',
  navigation: {
    ariaLabel: 'Main navigation',
    home: 'Panel',
    apiDocs: 'API docs',
  },
  panel: {
    waterAriaLabel: (liters: number) => `Daily water consumption: ${liters} litres`,
    statusSummary: (activeRows: number, displayMode: string) =>
      `${activeRows} of 5 bucket rows · ${displayMode} display`,
    waterSection: 'Daily water consumption',
    litersLabel: (liters: number) => `Litres: ${liters}`,
    litersInputLabel: 'Consumed litres',
    waterSubmit: 'Update water',
    displaySection: 'Display controls',
    rainbow: 'Rainbow',
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
        description: 'Updates daily consumed litres. Accepts integer-compatible numbers from 0 to 999.',
      },
      {
        methods: ['GET'],
        endpoint: '/api/status',
        request: 'None',
        description: 'Returns litres, active bucket rows, display dimensions, rotation, hardware type, and last update information.',
      },
      {
        methods: ['POST'],
        endpoint: '/api/rainbow',
        request: '{"brightness": 1, "speed": 0.1}',
        description: 'Starts the hardware validation rainbow. Brightness and speed are optional.',
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
