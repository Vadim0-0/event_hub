const PRIVATE_ROUTES = [
  '/main',
  // '/profile'
];

const GUEST_ONLY_ROUTES = [
  '/auth'
];

const LOCALE_PREFIXES = ['ru'];

function normalizePath(path: string) {
  const segments = path.split('/').filter(Boolean);

  if (segments[0] && LOCALE_PREFIXES.includes(segments[0])) {
    return '/' + segments.slice(1).join('/')
  };

  return path || '/';
}

function matchesRoute(path: string, routes: string[]) {
  return routes.some(
    (route) => path === route || path.startsWith(`${route}/`),
  );
};

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return navigateTo('/auth')
  };
  
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return navigateTo('/main')
  };
});