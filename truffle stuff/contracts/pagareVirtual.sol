// pragma solidity ^0.5.16;
// pragma solidity ^0.6.4;
pragma solidity >=0.5.16 <0.7.0;


contract PagareVirtual {
    string id = "cccc";

    function setId(string memory serial) public {
        id = serial;
    }

    function getId() public view returns (string memory) {
        return id;
    }

    // Numero de apgares general
    uint256 numPagares;
    // Numero endosos general
    uint256 numEndosos;

    constructor() public {
        numPagares = 0;
        numEndosos = 1;
    }

    // Numero de pagares de un deudor como deudor
    mapping(address => uint256) pagareDeudorCount;
    // numero de pagares en como acreedor para el address x
    mapping(address => uint256) pagareAcreedorCount;

    //Info tiene las variables: fecha_creacion,fecha_vencimiento,fecha_expiracion,lugar_creacion,lugar_cumplimiento,firma
    struct Pagare {
        uint256 _id;
        uint256 valorWei;
        address id_deudor;
        address id_acreedor;
        string info;
        bool firmado;
        uint256 ultimo_endoso;
        uint256 fecha_creacion;
        uint256 fecha_vencimiento;
        bool activo;
    }

    struct Endoso {
        uint256 _id;
        uint256 id_anterior_endoso;
        address id_endosante;
        address id_endosatario;
        uint256 id_pagare;
        uint256 fecha;
        bool es_ultimo_endoso;
    }

    mapping(uint256 => Pagare) private pagareStore;

    mapping(uint256 => Endoso) private endosoStore;

    //[id_acreedor][id_pagare]
    mapping(address => mapping(uint256 => bool)) private acreedorStore;

    //[id_deudor][id_pagare]
    mapping(address => mapping(uint256 => bool)) private deudorStore;

    event PagareCreate(
        uint256 _id,
        address deudor_id,
        address acreedor_id,
        uint256 valor
    );
    event RejectCreate(string _id, string message);
    event AcceptEndoso(
        address from,
        address to,
        uint256 _id,
        uint256 id_endoso
    );
    event RejectEndoso(string from, string to, string _id, string message);

    function createPagare(
        address id_deudor,
        string memory info,
        uint256 fecha_creacion,
        uint256 fecha_vencimiento
    ) public payable {
        uint256 _id = numPagares;
        numPagares++;
        pagareStore[_id] = Pagare(
            _id,
            msg.value,
            id_deudor,
            msg.sender,
            info,
            false,
            0,
            fecha_creacion,
            fecha_vencimiento,
            false //activo
        );
        acreedorStore[msg.sender][_id] = true;
        deudorStore[id_deudor][_id] = true;
        pagareDeudorCount[id_deudor]++;
        pagareAcreedorCount[msg.sender]++;
        emit PagareCreate(_id, id_deudor, msg.sender, msg.value);
    }

    function firmarPagare(uint256 _id) public {
        require(
            msg.sender == pagareStore[_id].id_deudor,
            "El que quiere firmar no es quien aparece como deudor"
        );
        require(pagareStore[_id].firmado == false, "El pagare ya esta firmado");
        msg.sender.transfer(pagareStore[_id].valorWei);
        pagareStore[_id].firmado = true;
        pagareStore[_id].activo = true;
    }

    function endosarPagare(
        address id_endosatario,
        uint256 id_pagare,
        uint256 fecha
    ) public {
        address id_endosante = msg.sender;
        uint256 id_endoso = numEndosos;
        numEndosos++;
        require(
            acreedorStore[msg.sender][id_pagare],
            "El endosante no es el legitimo tenedor del pagare"
        );
        require(
            pagareStore[id_pagare].activo,
            "El pagare no esta activo o no ha sido firmado"
        );
        endosoStore[id_endoso] = Endoso(
            id_endoso,
            pagareStore[id_pagare].ultimo_endoso,
            id_endosante,
            id_endosatario,
            id_pagare,
            fecha,
            true
        );
        endosoStore[pagareStore[id_pagare].ultimo_endoso]
            .es_ultimo_endoso = false;
        pagareStore[id_pagare].ultimo_endoso = id_endoso;
        acreedorStore[id_endosante][id_pagare] = false;
        acreedorStore[id_endosatario][id_pagare] = true;
        emit AcceptEndoso(id_endosante, id_endosatario, id_pagare, id_endoso);
    }

    function getPagareById(uint256 _id)
        public
        view
        returns (
            uint256,
            address,
            address,
            string memory,
            bool,
            uint256,
            uint256
        )
    {
        return (
            pagareStore[_id].valorWei,
            pagareStore[_id].id_deudor,
            pagareStore[_id].id_acreedor,
            pagareStore[_id].info,
            pagareStore[_id].firmado,
            pagareStore[_id].fecha_creacion,
            pagareStore[_id].fecha_vencimiento
        );
    }

    function getEndosoById(uint256 _id)
        public
        view
        returns (uint256, uint256, address, address, uint256, uint256, bool)
    {
        return (
            endosoStore[_id]._id,
            endosoStore[_id].id_anterior_endoso,
            endosoStore[_id].id_endosante,
            endosoStore[_id].id_endosatario,
            endosoStore[_id].id_pagare,
            endosoStore[_id].fecha,
            endosoStore[_id].es_ultimo_endoso
        );
    }

    function esAcreedorDe(address owner, uint256 _id)
        public
        view
        returns (bool)
    {
        if (acreedorStore[owner][_id]) {
            return true;
        }

        return false;
    }

    function esDeudorDe(address owner, uint256 _id) public view returns (bool) {
        if (deudorStore[owner][_id]) {
            return true;
        }

        return false;
    }

    function getIdPagaresDeudor(address deudor)
        public
        view
        returns (uint256[] memory)
    {
        uint256[] memory ret = new uint256[](pagareDeudorCount[deudor]);
        uint256 j = 0;
        for (uint256 i = 0; i < numPagares; i++) {
            if (deudorStore[deudor][i]) {
                ret[j] = pagareStore[i]._id;
                j++;
            }
        }
        return ret;
    }

    function getIdPagaresAcreedor(address acreedor)
        public
        view
        returns (uint256[] memory)
    {
        uint256[] memory ret = new uint256[](pagareAcreedorCount[acreedor]);
        uint256 j = 0;
        for (uint256 i = 0; i < numPagares; i++) {
            if (esAcreedorDe(acreedor, i)) {
                ret[j] = pagareStore[i]._id;
                j++;
            }
        }
        return ret;
    }

    function devolverDinero(uint256 _id) public {
        require(
            msg.sender == pagareStore[_id].id_acreedor,
            "Quien lo llama no es el acreedor del pagare"
        );
        require(pagareStore[_id].firmado == false, "Ya fue firmado el pagare");
        uint256 ahora = block.timestamp;
        uint256 diff = ahora - pagareStore[_id].fecha_creacion;
        uint256 segundos2dias = 2 * 24 * 60 * 60;
        require(diff > segundos2dias, "No han pasado 2 dias aun");
        deudorStore[pagareStore[_id].id_deudor][_id] = false;
        acreedorStore[msg.sender][_id] = false;
        pagareDeudorCount[pagareStore[_id].id_deudor] --;
        pagareAcreedorCount[msg.sender] --;
        pagareStore[_id].id_deudor = 0x0000000000000000000000000000000000000000;
        pagareStore[_id].id_acreedor = 0x0000000000000000000000000000000000000000;
        msg.sender.transfer(pagareStore[_id].valorWei);
        pagareStore[_id].valorWei = 0;
    }

    function getEndososPagare(uint256 _id)
        public
        view
        returns (uint256[] memory)
    {
        uint256 nEndosos = 0;
        uint256 currentEndoso = pagareStore[_id].ultimo_endoso;
        while (currentEndoso > 0) {
            nEndosos++;
            currentEndoso = endosoStore[currentEndoso].id_anterior_endoso;
        }
        uint256[] memory ret = new uint256[](nEndosos);
        currentEndoso = pagareStore[_id].ultimo_endoso;
        for (uint256 i = 0; i < nEndosos; i++) {
            ret[i] = currentEndoso;
            currentEndoso = endosoStore[currentEndoso].id_anterior_endoso;
        }
        return ret;
    }
}
