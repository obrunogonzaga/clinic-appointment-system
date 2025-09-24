const clamp = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max);

const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const normalized = hex.replace('#', '');
  if (normalized.length !== 6) {
    return null;
  }

  const r = parseInt(normalized.substring(0, 2), 16);
  const g = parseInt(normalized.substring(2, 4), 16);
  const b = parseInt(normalized.substring(4, 6), 16);

  if ([r, g, b].some((component) => Number.isNaN(component))) {
    return null;
  }

  return { r, g, b };
};

export const getReadableTextColor = (hex: string): string => {
  const rgb = hexToRgb(hex);
  if (!rgb) {
    return '#111827'; // Slate-900 fallback
  }

  // Relative luminance (WCAG)
  const { r, g, b } = rgb;
  const [rl, gl, bl] = [r, g, b].map((component) => {
    const channel = component / 255;
    return channel <= 0.03928
      ? channel / 12.92
      : Math.pow((channel + 0.055) / 1.055, 2.4);
  });

  const luminance = 0.2126 * rl + 0.7152 * gl + 0.0722 * bl;
  return luminance > 0.5 ? '#1f2937' : '#ffffff';
};

export const withAlpha = (hex: string, alpha: number): string => {
  const normalizedAlpha = clamp(alpha, 0, 1);
  const alphaHex = Math.round(normalizedAlpha * 255)
    .toString(16)
    .padStart(2, '0');
  const cleanHex = hex.startsWith('#') ? hex.slice(1) : hex;
  if (cleanHex.length !== 6) {
    return hex;
  }
  return `#${cleanHex}${alphaHex}`;
};
