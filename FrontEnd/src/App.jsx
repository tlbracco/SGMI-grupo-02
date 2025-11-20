import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css';

//imports de cada pagina
import Grupo from "./pages/grupo/Grupo.jsx";
import Inventario from "./pages/inventario e infraestructura/Inventario.jsx";
import Login from "./pages/login/Login.jsx";
import Planificacion from "./pages/planificacion/Planificacion.jsx";
import Proyecto from "./pages/proyectos/Proyecto.jsx";


function App() {
  	return (
		<Router>
			<Routes>
				<Route path="/grupo" element={ <Grupo/> }></Route>
				<Route path="/grupo/planificacion/inventario" element={ <Inventario/> }></Route>
				<Route path="/login" element={ <Login/> }></Route>
				<Route path="/grupo/planificacion" element={ <Planificacion/> }></Route>
				<Route path="/grupo/planificacion/proyecto" element={ <Proyecto/> }></Route>
			</Routes>
		</Router>
  	)
}

export default App
