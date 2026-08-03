import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../services/api";
import { requestOnboardingAfterLogin } from "../../utils/onboarding";


export default function Register() {

  const navigate = useNavigate();


  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);


  async function handleRegister(
    e: React.FormEvent
  ) {

    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {

      await api.post(
        "/users/register",
        {
          email,
          password,
          accept_terms: acceptTerms,
        }
      );


      setMessage(
        "Account created successfully"
      );
      setPassword("");

      requestOnboardingAfterLogin();

      setTimeout(() => {

        navigate("/login");

      }, 1000);


    } catch (error: any) {

      if (
        error.response?.status === 409
      ) {

        setError(
          "User already exists"
        );

      } else {

        setError(
          error.response?.status === 422
            ? "Enter a valid email and a password with at least 8 characters."
            : "Registration is temporarily unavailable. Please try again."
        );

      }

    } finally {
      setLoading(false);
    }

  }


  return (

    <div
      className="
        min-h-screen
        flex
        items-center
        justify-center
        bg-gray-50
      "
    >

      <form
        onSubmit={handleRegister}
        className="
          bg-white
          p-8
          rounded-xl
          shadow
          w-96
        "
      >

        <h1
          className="
            text-2xl
            font-bold
            mb-6
          "
        >
          Create Account
        </h1>


        {error && (

          <p
            role="alert"
            className="
              text-red-500
              mb-4
            "
          >
            {error}
          </p>

        )}


        {message && (

          <p
            role="status"
            className="
              text-green-600
              mb-4
            "
          >
            {message}
          </p>

        )}


        <input
          className="
            border
            p-3
            w-full
            mb-4
            rounded
          "
          placeholder="Email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={
            e => setEmail(e.target.value)
          }
        />

        <label className="mb-6 flex items-start gap-3 text-sm text-gray-700">
          <input type="checkbox" checked={acceptTerms} onChange={(event) => setAcceptTerms(event.target.checked)} required className="mt-1" />
          <span>I agree to the <a href="/terms" target="_blank" className="font-semibold underline">Terms of Use</a> and acknowledge the <a href="/privacy" target="_blank" className="font-semibold underline">Privacy Notice</a>.</span>
        </label>


        <input
          className="
            border
            p-3
            w-full
            mb-6
            rounded
          "
          placeholder="Password"
          type="password"
          required
          minLength={8}
          maxLength={128}
          autoComplete="new-password"
          value={password}
          onChange={
            e => setPassword(e.target.value)
          }
        />


        <button
          type="submit"
          disabled={!acceptTerms || loading}
          className="
            bg-black
            text-white
            w-full
            p-3
            rounded
            disabled:cursor-wait
            disabled:opacity-60
          "
        >
          {loading ? "Creating account..." : "Register"}
        </button>


      </form>


    </div>

  );
}
