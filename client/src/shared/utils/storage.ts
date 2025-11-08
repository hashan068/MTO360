export const safeLocalStorage = typeof window !== 'undefined' ? window.localStorage : undefined;

type StorageValue = string | null;

export function getItem(key: string): StorageValue {
  try {
    return safeLocalStorage?.getItem(key) ?? null;
  } catch (error) {
    console.warn('[storage] Unable to read key', key, error);
    return null;
  }
}

export function setItem(key: string, value: string): void {
  try {
    safeLocalStorage?.setItem(key, value);
  } catch (error) {
    console.warn('[storage] Unable to write key', key, error);
  }
}

export function removeItem(key: string): void {
  try {
    safeLocalStorage?.removeItem(key);
  } catch (error) {
    console.warn('[storage] Unable to remove key', key, error);
  }
}

export function clearAll(): void {
  try {
    safeLocalStorage?.clear();
  } catch (error) {
    console.warn('[storage] Unable to clear storage', error);
  }
}
