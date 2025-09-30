export const onlyDigits = (value: string | null | undefined): string => {
  if (!value) {
    return '';
  }
  return value.replace(/\D/g, '');
};

export const normalizeCpf = (value: string | null | undefined): string => {
  return onlyDigits(value);
};

export const isValidCpf = (value: string | null | undefined): boolean => {
  const digits = onlyDigits(value);
  if (digits.length !== 11) {
    return false;
  }

  if (/^(\d)\1{10}$/.test(digits)) {
    return false;
  }

  const calcCheckDigit = (sliceLength: number): number => {
    let total = 0;
    for (let index = 0; index < sliceLength; index += 1) {
      total += parseInt(digits.charAt(index), 10) * (sliceLength + 1 - index);
    }
    const remainder = (total * 10) % 11;
    return remainder === 10 ? 0 : remainder;
  };

  const firstCheck = calcCheckDigit(9);
  const secondCheck = calcCheckDigit(10);

  return (
    firstCheck === parseInt(digits.charAt(9), 10) &&
    secondCheck === parseInt(digits.charAt(10), 10)
  );
};

export const formatCpf = (value: string | null | undefined): string => {
  const digits = onlyDigits(value);
  if (digits.length !== 11) {
    return value?.trim() ?? '';
  }

  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
};

export const maskCpf = (value: string | null | undefined): string => {
  return formatCpf(value);
};
