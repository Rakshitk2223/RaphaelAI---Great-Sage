// Firebase service - handles Firebase app initialization and authentication
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";

// Your web app's Firebase configuration
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
const analytics = getAnalytics(app);
const auth = getAuth(app);

export { app, analytics, auth, firebaseConfig };
