import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AuthForm from "./components/AuthForm";
import HomePage from "./components/HomePage";
import "@fontsource/montserrat/800.css";
import "@fontsource/archivo-black";
import EditorPage from './components/EditorPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthForm />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/editor" element={<EditorPage />} />
      </Routes>
    </Router>    

    
  );
}

export default App;
