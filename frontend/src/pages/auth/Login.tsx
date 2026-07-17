import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
} from "lucide-react";

import api from "../../services/api";
import { useAuth } from "../../hooks/useAuth";


export default function Login() {

  const navigate = useNavigate();

  const { login } = useAuth();


  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleLogin(
    event: FormEvent<HTMLFormElement>,
  ) {

    event.preventDefault();

    setError("");
    setLoading(true);


    try {

      const response = await api.post(
        "/users/login",
        {
          email,
          password,
        },
      );


      login(
        response.data.access_token,
      );


      navigate(
        "/dashboard",
        {
          replace: true,
        },
      );

    } catch {

      setError(
        "Invalid email or password.",
      );

    } finally {

      setLoading(false);

    }

  }


  return (

    <main className="min-h-screen bg-gray-950 px-4 py-8 sm:px-6">

      <div className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-6xl items-center justify-center">

        <div className="grid w-full overflow-hidden rounded-3xl border border-gray-800 bg-gray-900 shadow-2xl lg:grid-cols-2">


          {/* Brand panel */}

          <section className="hidden min-h-[680px] flex-col justify-between bg-gradient-to-br from-blue-700 via-indigo-700 to-violet-800 p-10 lg:flex">

            <div>

              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-blue-100">
                NextHire AI
              </p>

              <h1 className="mt-8 max-w-lg text-5xl font-bold leading-tight text-white">
                Your next opportunity starts here.
              </h1>

              <p className="mt-5 max-w-md text-lg leading-8 text-blue-100">
                Build stronger resumes, identify skill gaps,
                prepare for interviews, and discover better
                career opportunities.
              </p>

            </div>


            <div className="grid grid-cols-2 gap-4">

              <MetricCard
                label="Resume insights"
                value="AI-powered"
              />

              <MetricCard
                label="Career profile"
                value="Personalized"
              />

              <MetricCard
                label="Job matching"
                value="Targeted"
              />

              <MetricCard
                label="Interview prep"
                value="Practical"
              />

            </div>

          </section>


          {/* Login panel */}

          <section className="flex min-h-[620px] items-center px-5 py-10 sm:px-10 lg:min-h-[680px] lg:px-14">

            <div className="mx-auto w-full max-w-md">

              <div className="lg:hidden">

                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-blue-400">
                  NextHire AI
                </p>

              </div>


              <h2 className="mt-5 text-3xl font-bold text-white sm:text-4xl">
                Welcome back
              </h2>

              <p className="mt-3 text-sm leading-6 text-gray-400 sm:text-base">
                Sign in to continue building your career.
              </p>


              <form
                onSubmit={handleLogin}
                className="mt-8 space-y-5"
              >

                {error && (

                  <div
                    role="alert"
                    className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300"
                  >
                    {error}
                  </div>

                )}


                <label className="block">

                  <span className="mb-2 block text-sm font-medium text-gray-300">
                    Email address
                  </span>

                  <div className="flex min-h-12 items-center gap-3 rounded-xl border border-gray-700 bg-gray-950 px-4 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">

                    <Mail
                      size={19}
                      className="shrink-0 text-gray-500"
                    />

                    <input
                      type="email"
                      value={email}
                      onChange={(event) =>
                        setEmail(event.target.value)
                      }
                      placeholder="you@example.com"
                      autoComplete="email"
                      required
                      className="min-w-0 flex-1 bg-transparent py-3 text-white outline-none placeholder:text-gray-600"
                    />

                  </div>

                </label>


                <label className="block">

                  <div className="mb-2 flex items-center justify-between gap-4">

                    <span className="text-sm font-medium text-gray-300">
                      Password
                    </span>

                    <Link
                      to="/forgot-password"
                      className="text-sm font-medium text-blue-400 transition hover:text-blue-300"
                    >
                      Forgot password?
                    </Link>

                  </div>


                  <div className="flex min-h-12 items-center gap-3 rounded-xl border border-gray-700 bg-gray-950 px-4 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">

                    <LockKeyhole
                      size={19}
                      className="shrink-0 text-gray-500"
                    />

                    <input
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      value={password}
                      onChange={(event) =>
                        setPassword(event.target.value)
                      }
                      placeholder="Enter your password"
                      autoComplete="current-password"
                      required
                      className="min-w-0 flex-1 bg-transparent py-3 text-white outline-none placeholder:text-gray-600"
                    />

                    <button
                      type="button"
                      onClick={() =>
                        setShowPassword(
                          (currentValue) =>
                            !currentValue,
                        )
                      }
                      aria-label={
                        showPassword
                          ? "Hide password"
                          : "Show password"
                      }
                      className="rounded-lg p-1 text-gray-500 transition hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >

                      {showPassword
                        ? <EyeOff size={19} />
                        : <Eye size={19} />
                      }

                    </button>

                  </div>

                </label>


                <label className="flex items-center gap-3 text-sm text-gray-400">

                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-600 bg-gray-950 text-blue-600 focus:ring-blue-500"
                  />

                  Keep me signed in

                </label>


                <button
                  type="submit"
                  disabled={loading}
                  className="
                    inline-flex
                    min-h-12
                    w-full
                    items-center
                    justify-center
                    gap-2
                    rounded-xl
                    bg-blue-600
                    px-5
                    py-3
                    font-semibold
                    text-white
                    transition
                    hover:bg-blue-500
                    focus:outline-none
                    focus:ring-2
                    focus:ring-blue-400
                    focus:ring-offset-2
                    focus:ring-offset-gray-900
                    disabled:cursor-not-allowed
                    disabled:opacity-60
                  "
                >

                  {loading
                    ? "Signing in..."
                    : "Sign in"
                  }

                  {!loading && (
                    <ArrowRight size={19} />
                  )}

                </button>

              </form>


              <p className="mt-7 text-center text-sm text-gray-400">

                Don&apos;t have an account?{" "}

                <Link
                  to="/register"
                  className="font-semibold text-blue-400 transition hover:text-blue-300"
                >
                  Create an account
                </Link>

              </p>

            </div>

          </section>

        </div>

      </div>

    </main>

  );

}


function MetricCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (

    <div className="rounded-2xl border border-white/15 bg-white/10 p-5 backdrop-blur">

      <p className="text-sm text-blue-100">
        {label}
      </p>

      <p className="mt-2 text-lg font-semibold text-white">
        {value}
      </p>

    </div>

  );

}
