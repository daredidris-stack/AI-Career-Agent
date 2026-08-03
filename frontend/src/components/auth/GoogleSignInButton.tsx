import { useEffect, useRef } from "react";


type GoogleCredentialResponse = {
  credential: string;
};


type GoogleIdentityApi = {
  initialize: (options: {
    client_id: string;
    callback: (response: GoogleCredentialResponse) => void;
    ux_mode?: "popup" | "redirect";
  }) => void;
  renderButton: (
    parent: HTMLElement,
    options: {
      type: "standard";
      theme: "outline" | "filled_blue" | "filled_black";
      size: "large";
      text: "continue_with";
      shape: "rectangular";
      logo_alignment: "left";
      width: number;
    },
  ) => void;
};


declare global {
  interface Window {
    google?: {
      accounts: {
        id: GoogleIdentityApi;
      };
    };
  }
}


const googleScriptId = "google-identity-services";
const googleScriptUrl = "https://accounts.google.com/gsi/client";
let initializedGoogleClientId = "";
let activeCredentialHandler:
  | ((response: GoogleCredentialResponse) => void)
  | null = null;


export default function GoogleSignInButton({
  clientId,
  disabled = false,
  onCredential,
  onError,
}: {
  clientId: string;
  disabled?: boolean;
  onCredential: (credential: string) => void;
  onError: () => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!clientId || !container) {
      return;
    }

    let active = true;
    const handleCredential = (response: GoogleCredentialResponse) => {
      if (response.credential) {
        onCredential(response.credential);
      } else {
        onError();
      }
    };
    activeCredentialHandler = handleCredential;

    const renderButton = () => {
      if (!active || !window.google) {
        return;
      }

      container.replaceChildren();
      if (initializedGoogleClientId !== clientId) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: (response) => activeCredentialHandler?.(response),
          ux_mode: "popup",
        });
        initializedGoogleClientId = clientId;
      }
      window.google.accounts.id.renderButton(
        container,
        {
          type: "standard",
          theme: "filled_black",
          size: "large",
          text: "continue_with",
          shape: "rectangular",
          logo_alignment: "left",
          width: Math.min(
            400,
            Math.max(240, container.clientWidth),
          ),
        },
      );
    };

    let script = document.getElementById(
      googleScriptId,
    ) as HTMLScriptElement | null;
    if (!script) {
      script = document.createElement("script");
      script.id = googleScriptId;
      script.src = googleScriptUrl;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    }

    script.addEventListener("load", renderButton);
    script.addEventListener("error", onError);
    if (window.google) {
      renderButton();
    }

    return () => {
      active = false;
      script?.removeEventListener("load", renderButton);
      script?.removeEventListener("error", onError);
      if (activeCredentialHandler === handleCredential) {
        activeCredentialHandler = null;
      }
      container.replaceChildren();
    };
  }, [clientId, onCredential, onError]);

  return (
    <div
      className={disabled ? "pointer-events-none opacity-60" : ""}
      aria-busy={disabled}
    >
      <div ref={containerRef} className="flex min-h-11 justify-center" />
    </div>
  );
}
