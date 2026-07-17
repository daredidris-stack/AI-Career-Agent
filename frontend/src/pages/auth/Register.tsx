import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../services/api";


export default function Register() {

  const navigate = useNavigate();


  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");


  async function handleRegister(
    e: React.FormEvent
  ) {

    e.preventDefault();


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
          "Registration failed"
        );

      }

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
          value={password}
          onChange={
            e => setPassword(e.target.value)
          }
        />


        <button
          disabled={!acceptTerms}
          className="
            bg-black
            text-white
            w-full
            p-3
            rounded
          "
        >
          Register
        </button>


      </form>


    </div>

  );
}
