import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import {
  getAccessToken,
  removeAccessToken,
  setAccessToken,
} from "../services/api";


interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}


const AuthContext =
  createContext<AuthContextType | null>(
    null
  );


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


export function useAuth() {

  const context =
    useContext(AuthContext);


  if (!context) {

    throw new Error(
      "useAuth must be used inside AuthProvider"
    );

  }


  return context;

}