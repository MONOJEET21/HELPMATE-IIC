import React,{createContext,useContext,useState} from 'react'
import api from './api'
const C=createContext(null)
export function AuthProvider({children}){
 const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('hm_user'))}catch{return null}})
 async function save(path,payload){const {data}=await api.post(path,payload);localStorage.setItem('hm_token',data.access_token);localStorage.setItem('hm_user',JSON.stringify(data.user));setUser(data.user)}
 const login=(email,password)=>save('/api/auth/login',{email,password})
 const register=payload=>save('/api/auth/register',payload)
 function logout(){localStorage.removeItem('hm_token');localStorage.removeItem('hm_user');setUser(null)}
 return <C.Provider value={{user,login,register,logout}}>{children}</C.Provider>
}
export const useAuth=()=>useContext(C)
