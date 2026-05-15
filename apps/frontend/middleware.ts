import { NextRequest, NextResponse } from "next/server";

const AUTH_COOKIE_NAMES = ["sessionid"];
const PROTECTED_PREFIX = "/dashboard";

function hasLikelyAuthCookie(request: NextRequest) {
  return AUTH_COOKIE_NAMES.some((cookieName) => Boolean(request.cookies.get(cookieName)?.value));
}

function isProtectedPath(pathname: string) {
  return pathname === PROTECTED_PREFIX || pathname.startsWith(`${PROTECTED_PREFIX}/`);
}

export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (!isProtectedPath(pathname) || hasLikelyAuthCookie(request)) {
    return NextResponse.next();
  }

  const loginUrl = request.nextUrl.clone();
  loginUrl.pathname = "/login";
  loginUrl.search = "";
  loginUrl.searchParams.set("redirect", `${pathname}${search}`);

  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/dashboard/:path*"],
};

