import React from "react";
import { useParams } from "react-router-dom"
import "./Grupo.css";


import CabeceraTabla from "../../components/CabeceraTabla";
import Tabla from "../../components/Tabla";
import Boton from "../../components/Boton";


function Grupo() {

    const columnas = ["Sigla", "Nombre", "Unidad Academica", "Director/a", "Vicedirector/a", "Correo Electronico"];
    const filasPrueba = [
        ["S.M.O.P", "Smooth Operator", "Ferrari", "Carlos Sainz JR.", "Charles Leclerc", "ferrari@gmail.com"],
        ["L.I.N.S.I", "Laboratorio de ingenieria en sistemas de informacion", "frlp", "Milagros Crespo", "Martina Garcia", "linsi@hotmail.com"]
    ];

    const agregar = "agregar grupo";

    function agregarGrupo(){
        console.log("agregar grupo");
    }

    return (
        <div>
            <div>
                <h1>aca va el header</h1>
            </div>
            <div>
                <div className="row container-fluid">
                    <h1 className="col-2">Grupos:</h1>
                    <div className="col-8"></div>
                    <div className="col-2">
                        <Boton texto={agregar} accion={agregarGrupo}></Boton>
                    </div>
                </div>
                <div className="row container-fluid">
                    <div className="col-1"></div>
                    <div className="col-10">
                        <Tabla 
                            columnas={columnas}
                            filas={filasPrueba}
                        >
                        </Tabla>
                    </div>
                    <div className="col-1"></div>
                </div>
            </div>
        </div>
    )
}

export default Grupo