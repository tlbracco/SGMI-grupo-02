import React from "react";
import Button from "react-bootstrap/Button";


function Boton({texto, accion}){
    return (
        <Button
            variant="primary"
            type="button"
            onClick={()=>accion()}
        >
            {texto}
        </Button>
    )
}

export default Boton;