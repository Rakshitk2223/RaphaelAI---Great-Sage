// Firebase configuration and initialization
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBEQopN9GYBAGkRUm0vgrn3farGVanJnDU",
  authDomain: "raphael-great-sage.firebaseapp.com",
  projectId: "raphael-great-sage",
  storageBucket: "raphael-great-sage.firebasestorage.app",
  messagingSenderId: "304693749680",
  appId: "1:304693749680:web:a35d6bdd9aed97e6abd875",
  measurementId: "G-EBN033R0M1"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };
