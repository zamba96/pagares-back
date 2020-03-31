pragma solidity ^0.5.16;
// pragma solidity ^0.6.4;

contract PagareTracker {
    string id = "aaa";

    function setId(string memory serial) public {
        id = serial;
    }

    function getId() public view returns (string memory) {
        return id;
    }

    //Info tiene las variables: fecha_creacion,fecha_vencimiento,fecha_expiracion,lugar_creacion,lugar_cumplimiento,firma
    struct Pagare {
        string _id;
        string valor;
        string id_deudor;
        string id_acreedor;
        string info;
        bool pendiente;
        string ultimo_endoso;
    }

    struct Endoso {
        string _id;
        string id_anterior_endoso;
        string id_endosante;
        string id_endosatario;
        string id_pagare;
        string fecha;
        string firma;
    }

    mapping(string => Pagare) private pagareStore;

    mapping(string => Endoso) private endosoStore;

    //[id_acreedor][id_pagare]
    mapping(string => mapping(string => bool)) private acreedorStore;

    //[id_deudor][id_pagare]
    mapping(string => mapping(string => bool)) private deudorStore;

    event PagareCreate(
        string _id,
        string deudor_id,
        string acreedor_id,
        string valor
    );
    event RejectCreate(string _id, string message);
    event PagareEndoso(string from, string to, string _id);
    event RejectEndoso(string from, string to, string _id, string message);

    function createPagare(
        string memory _id,
        string memory valor,
        string memory id_deudor,
        string memory id_acreedor,
        string memory info
    ) public {
        if (!(bytes(pagareStore[_id]._id).length == 0)) {
            return;
        }
        pagareStore[_id] = Pagare(
            _id,
            valor,
            id_deudor,
            id_acreedor,
            info,
            true,
            "null"
        );
        acreedorStore[id_acreedor][_id] = true;
        deudorStore[id_deudor][_id] = true;
        emit PagareCreate(_id, id_deudor, id_acreedor, valor);
    }

    function transferPagare(
        string memory id_endosante,
        string memory id_endosatario,
        string memory _id,
        string memory fecha,
        string memory firma,
        string memory id_endoso
    ) public {
        if (!pagareStore[_id].pendiente) {
            emit RejectEndoso(
                id_endosante,
                id_endosatario,
                _id,
                "No existe el pagare con el id, o ya fue pagado"
            );
            return;
        }

        if (!acreedorStore[id_endosante][_id]) {
            emit RejectEndoso(
                id_endosante,
                id_endosatario,
                _id,
                "El endosante no tiene el pagare con el id"
            );
            return;
        }
        endosoStore[id_endoso] = Endoso(
            id_endoso,
            pagareStore[_id].ultimo_endoso,
            id_endosante,
            id_endosatario,
            _id,
            fecha,
            firma
        );
        pagareStore[_id].ultimo_endoso = id_endoso;
        acreedorStore[id_endosante][_id] = false;
        acreedorStore[id_endosatario][_id] = true;
        emit PagareEndoso(id_endosante, id_endosatario, _id);
    }

    function getPagareById(string memory _id)
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory,
            string memory,
            string memory,
            bool
        )
    {
        // string _id, string valor, string id_deudor, string id_acreedor, string info, string firma
        return (
            pagareStore[_id]._id,
            pagareStore[_id].valor,
            pagareStore[_id].id_deudor,
            pagareStore[_id].id_acreedor,
            pagareStore[_id].info,
            pagareStore[_id].ultimo_endoso,
            pagareStore[_id].pendiente
        );
    }

    function getEndosoById(string memory _id)
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            string memory,
            string memory,
            string memory,
            string memory
        )
    {
        return (
            endosoStore[_id]._id,
            endosoStore[_id].id_anterior_endoso,
            endosoStore[_id].id_endosante,
            endosoStore[_id].id_endosatario,
            endosoStore[_id].id_pagare,
            endosoStore[_id].fecha,
            endosoStore[_id].firma
        );
    }

    function isOwnerOf(string memory owner, string memory _id)
        public
        view
        returns (bool)
    {
        if (acreedorStore[owner][_id]) {
            return true;
        }

        return false;
    }
}
