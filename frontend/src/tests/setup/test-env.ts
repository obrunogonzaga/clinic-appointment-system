const globalAny = globalThis as typeof globalThis & {
  window?: Record<string, unknown>;
  document?: Record<string, unknown>;
  navigator?: Record<string, unknown>;
};

if (!globalAny.window) {
  globalAny.window = {};
}

const windowAny = globalAny.window as Record<string, unknown> & {
  matchMedia?: (query: string) => MediaQueryList;
};

windowAny.ENV = windowAny.ENV ?? { API_URL: 'http://localhost:8000' };
windowAny.confirm = windowAny.confirm ?? (() => true);
windowAny.alert = windowAny.alert ?? (() => undefined);
windowAny.localStorage = windowAny.localStorage ?? {
  getItem: () => null,
  setItem: () => undefined,
  removeItem: () => undefined,
};
windowAny.location = windowAny.location ?? {
  href: 'http://localhost/dashboard',
  assign: () => undefined,
  replace: () => undefined,
};
windowAny.history = windowAny.history ?? {
  pushState: () => undefined,
  replaceState: () => undefined,
};

if (!windowAny.matchMedia) {
  windowAny.matchMedia = () => ({
    matches: false,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
    media: '',
    onchange: null,
  }) as unknown as MediaQueryList;
}

globalAny.document = globalAny.document ?? {
  documentElement: {
    classList: {
      add: () => undefined,
      remove: () => undefined,
    },
  },
};

globalAny.navigator = globalAny.navigator ?? { userAgent: 'node' };
