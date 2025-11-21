import React from "react";

function CabeceraTabla({arrayCampos}) {

    return (
        <thead>
            <tr>
                {arrayCampos.map((campo, index)=>(
                    <th key={index}>{campo}</th>
                ))}
            </tr>
        </thead>
    )
}

export default CabeceraTabla