import React from "react";

function Boton({texto, accion}){
    return (
        <button
            className="btn"
            type="button"
            onClick={()=>accion()}
        >
            {texto}
        </button>
    )
}

export default Boton;