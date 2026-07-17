import {
  useState,
  type ReactNode,
} from "react";

import {
  getAccessToken,
  removeAccessToken,
  setAccessToken,
} from "../services/api";

import { AuthContext } from "./auth-context";


export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {

  const [token, setToken] =
    useState<string | null>(
      getAccessToken()
    );


  function login(newToken: string) {

    setAccessToken(newToken);

    setToken(newToken);

  }


  function logout() {

    removeAccessToken();

    setToken(null);

  }


  return (

    <AuthContext.Provider
      value={{
        token,
        isAuthenticated: Boolean(token),
        login,
        logout,
      }}
    >

      {children}

    </AuthContext.Provider>

  );

}
