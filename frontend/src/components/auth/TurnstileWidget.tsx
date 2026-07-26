import { useEffect, useRef, useState } from "react";


const SCRIPT_ID = "cloudflare-turnstile-script";
const SCRIPT_URL = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

type TurnstileOptions = {
  sitekey: string;
  action: string;
  theme: "dark";
  size: "flexible";
  appearance: "always";
  "response-field": false;
  callback: (token: string) => void;
  "error-callback": () => void;
  "expired-callback": () => void;
};

type TurnstileApi = {
  render: (container: HTMLElement, options: TurnstileOptions) => string;
  remove: (widgetId: string) => void;
};

declare global {
  interface Window {
    turnstile?: TurnstileApi;
  }
}

let turnstileLoader: Promise<TurnstileApi> | undefined;

function loadTurnstile(): Promise<TurnstileApi> {
  if (window.turnstile) return Promise.resolve(window.turnstile);
  if (turnstileLoader) return turnstileLoader;

  turnstileLoader = new Promise((resolve, reject) => {
    const finishLoading = () => {
      if (window.turnstile) {
        resolve(window.turnstile);
      } else {
        reject(new Error("Cloudflare Turnstile did not initialize."));
      }
    };

    const existingScript = document.getElementById(SCRIPT_ID);
    if (existingScript) {
      existingScript.addEventListener("load", finishLoading, { once: true });
      existingScript.addEventListener(
        "error",
        () => reject(new Error("Cloudflare Turnstile failed to load.")),
        { once: true },
      );
      return;
    }

    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = SCRIPT_URL;
    script.async = true;
    script.defer = true;
    script.addEventListener("load", finishLoading, { once: true });
    script.addEventListener(
      "error",
      () => reject(new Error("Cloudflare Turnstile failed to load.")),
      { once: true },
    );
    document.head.appendChild(script);
  });

  return turnstileLoader;
}

type TurnstileWidgetProps = {
  siteKey: string;
  onTokenChange: (token: string) => void;
  onError: () => void;
};

export default function TurnstileWidget({
  siteKey,
  onTokenChange,
  onError,
}: TurnstileWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const onTokenChangeRef = useRef(onTokenChange);
  const onErrorRef = useRef(onError);
  const [loadFailed, setLoadFailed] = useState(false);

  useEffect(() => {
    onTokenChangeRef.current = onTokenChange;
    onErrorRef.current = onError;
  }, [onError, onTokenChange]);

  useEffect(() => {
    let cancelled = false;
    let widgetId: string | undefined;

    loadTurnstile()
      .then((turnstile) => {
        if (cancelled || !containerRef.current) return;

        widgetId = turnstile.render(containerRef.current, {
          sitekey: siteKey,
          action: "login",
          theme: "dark",
          size: "flexible",
          appearance: "always",
          "response-field": false,
          callback: (token) => onTokenChangeRef.current(token),
          "error-callback": () => {
            onTokenChangeRef.current("");
            onErrorRef.current();
          },
          "expired-callback": () => onTokenChangeRef.current(""),
        });
      })
      .catch(() => {
        if (cancelled) return;
        setLoadFailed(true);
        onErrorRef.current();
      });

    return () => {
      cancelled = true;
      if (widgetId && window.turnstile) {
        window.turnstile.remove(widgetId);
      }
    };
  }, [siteKey]);

  return (
    <div className="space-y-2">
      <div ref={containerRef} className="min-h-[65px] w-full" />
      {loadFailed && (
        <p className="text-sm text-red-300">
          The security check could not load. Refresh the page and try again.
        </p>
      )}
    </div>
  );
}
