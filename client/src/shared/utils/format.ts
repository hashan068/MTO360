const defaultLocale = typeof navigator !== 'undefined' ? navigator.language : 'en-US';

export const formatCurrency = (value: number | string, currency = 'USD') => {
  const amount = typeof value === 'string' ? Number(value) : value;
  return new Intl.NumberFormat(defaultLocale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(Number.isFinite(amount) ? amount : 0);
};

export const formatNumber = (value: number | string, fractionDigits = 0) => {
  const amount = typeof value === 'string' ? Number(value) : value;
  return new Intl.NumberFormat(defaultLocale, {
    maximumFractionDigits: fractionDigits,
    minimumFractionDigits: fractionDigits,
  }).format(Number.isFinite(amount) ? amount : 0);
};

export const formatDate = (value: string | Date) => {
  const date = typeof value === 'string' ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return new Intl.DateTimeFormat(defaultLocale, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  }).format(date);
};
