import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import api from "../../services/api";
import { AuthCard } from "./ForgotPassword";


export default function VerifyEmail() {
  const [params] = useSearchParams();
  const [message, setMessage] = useState("Verifying your email...");
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    api.post("/auth/verification/confirm", { token: params.get("token") || "" })
      .then((response) => setMessage(response.data.message))
      .catch((error) => {
        setFailed(true);
        setMessage(error.response?.data?.detail || "Email verification failed.");
      });
  }, [params]);

  return (
    <AuthCard title="Email verification" description={message}>
      <Link to="/login" className="block rounded-xl bg-blue-600 px-4 py-3 text-center font-semibold text-white">{failed ? "Return to login" : "Continue to login"}</Link>
    </AuthCard>
  );
}
