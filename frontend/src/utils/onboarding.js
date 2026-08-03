const ONBOARDING_AFTER_LOGIN_KEY = "nexthire:onboarding-after-login";

export function requestOnboardingAfterLogin() {
  try {
    sessionStorage.setItem(ONBOARDING_AFTER_LOGIN_KEY, "true");
  } catch {
    // A restricted browser can still use the normal dashboard route.
  }
}

export function consumeOnboardingAfterLogin() {
  try {
    const requested = (
      sessionStorage.getItem(ONBOARDING_AFTER_LOGIN_KEY) === "true"
    );
    sessionStorage.removeItem(ONBOARDING_AFTER_LOGIN_KEY);
    return requested;
  } catch {
    return false;
  }
}
