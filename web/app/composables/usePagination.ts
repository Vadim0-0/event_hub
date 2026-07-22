export type PaginationItem = number | 'ellipsis';

export function getPaginationItems(current: number, total: number): PaginationItem[] {
  if (total <= 6) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  if (current <= 3) {
    return [1, 2, 3, 'ellipsis', total - 2, total - 1, total]
  }
  if (current >= total - 2) {
    return [1, 2, 3, 'ellipsis', total - 2, total - 1, total]
  }
  return [1, 2, 3, 'ellipsis', current - 1, current, current + 1, 'ellipsis', total - 2, total - 1, total]
};