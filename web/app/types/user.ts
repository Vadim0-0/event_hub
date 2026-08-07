export interface User {
  id: number
  username: string
  email: string
  created_at?: string
}

export interface UserListItem {
  id: number
  username: string
  email: string
  created_at: string
  is_me: boolean
};

export interface UsersCount {
  total: number
};