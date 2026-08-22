export interface Creator {
  id: number
  username: string
};

export interface Event {
  id: string
  creator: Creator
  title: string
  description: string | null
  starts_at: string
  location?: string | null
  latitude?: number | null
  longitude?: number | null
  max_participants: number | null
  participants_count: number
  created_at: string
};

export interface EventsCount {
  total: number
};

export interface EventDetail extends Event {
  is_participant: boolean | null
  is_creator: boolean | null
};

export interface Participant {
  user: {
    id: number
    username: string
    email: string
    created_at: string
  };
  
  registered_at: string
};