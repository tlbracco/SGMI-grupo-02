import React from "react";
import CabeceraTabla from "./CabeceraTabla";
import Table from "react-bootstrap/Table"

function Tabla({columnas, filas}) {
    return (
        <Table striped>
            <CabeceraTabla arrayCampos={columnas}></CabeceraTabla>
            <tbody>
                {filas.map((fila, index) => (
                    <tr key={index}>
                        {fila.map((celda, celdaIndex) => (
                            <td key={celdaIndex}>{celda}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </Table>
    )
}

export default Tabla