export type UserRole = 'ADMIN' | 'MANAGER' | 'SALES' | 'INVENTORY' | 'MANUFACTURING' | 'GUEST';

export interface UserSummary {
  id: number;
  username: string;
  email?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  role?: UserRole;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  token_type?: string;
}
