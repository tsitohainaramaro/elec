// ==========================================================
// GESTION ELECTRICITE
// ==========================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("===== APP.JS CHARGÉ =====");

    // LUCIDE

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

    // SIDEBAR MOBILE

    const menuButton = document.getElementById("menuButton");
    const sidebar = document.getElementById("sidebar");
    const sidebarOverlay = document.getElementById("sidebarOverlay");

    if (menuButton && sidebar) {

        menuButton.addEventListener("click", function () {
            sidebar.classList.toggle("-translate-x-full");

            if (sidebarOverlay) {
                sidebarOverlay.classList.toggle("hidden");
            }
        });
    }

    if (sidebarOverlay) {

        sidebarOverlay.addEventListener("click", function () {

            if (sidebar) {
                sidebar.classList.add("-translate-x-full");
            }

            sidebarOverlay.classList.add("hidden");
        });
    }

    // STOCKAGE DES GRAPHIQUES

    const graphiques = {};


    // ======================================================
    // OUTILS
    // ======================================================

    function nombre(valeur, decimals = 3) {

        const n = Number(valeur);

        if (isNaN(n)) {
            return "0";
        }

        return n.toFixed(decimals);
    }


    function formaterDate(date) {

        if (!date) {
            return "-";
        }

        const d = new Date(date);

        if (isNaN(d.getTime())) {
            return date;
        }

        return d.toLocaleString("fr-FR", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });
    }


    function actualiserElement(element, valeur) {

        if (!element) {
            return;
        }

        element.textContent = valeur;
    }


    // ======================================================
    // STATUT CLIENT
    // ======================================================

    // function afficherStatutTempsReel(compteurs) {

    //     const statut = document.getElementById("tempsReelStatut");

    //     if (!statut) {
    //         return;
    //     }

    //     if (!Array.isArray(compteurs) || compteurs.length === 0) {

    //         statut.textContent = "● Aucun compteur";
    //         return;
    //     }

    //     const connectes = compteurs.filter(
    //         compteur => compteur.esp32_connecte === true
    //     ).length; 

    //     if (connectes > 0) {

    //         statut.textContent =
    //             "● Temps réel actif — " +
    //             connectes +
    //             " compteur(s) connecté(s)";

    //     } else {

    //         statut.textContent =
    //             "● Aucun ESP32 connecté";
    //     }
    // }



    // ======================================================
    // DASHBOARD CLIENT
    // ======================================================

    function mettreAJourDashboard(compteurs) {

        if (!Array.isArray(compteurs)) {
            return;
        }


        // CALCUL GLOBAL CLIENT

        let soldeTotal = 0;
        let consommationTotal = 0;
        let compteursConnectes = 0;


        compteurs.forEach(function (compteur) {

            // CALCULS GLOBAUX

            soldeTotal += Number(
                compteur.solde || 0
            );


            consommationTotal += Number(
                compteur.consommation_totale || 0
            );


            if (
                compteur.esp32_connecte === true
            ) {

                compteursConnectes++;
            }


            // DEVICE ID

            const deviceId =
                compteur.device_id;

            if (!deviceId) {
                return;
            }

            // RECHERCHE DE LA CARTE

            const bloc = document.querySelector(
                `[data-device-id="${deviceId}"]`
            );

            // Si la carte n'existe pas encore,
            // on continue quand même les statistiques.
            if (!bloc) {
                return;
            }


            // SOLDE

            const solde =
                bloc.querySelector(
                    ".compteur-solde"
                );


            if (solde) {

                solde.textContent =
                    nombre(
                        compteur.solde,
                        3
                    );
            }


            // MESURE PZEM

            const mesure =
                compteur.mesure || null;


            if (mesure) {

                // PUISSANCE

                const puissance =
                    bloc.querySelector(
                        ".compteur-puissance"
                    );


                if (puissance) {

                    puissance.textContent =
                        nombre(
                            mesure.puissance,
                            1
                        );
                }


                // ÉNERGIE

                const energie =
                    bloc.querySelector(
                        ".compteur-energie"
                    );


                if (energie) {

                    energie.textContent =
                        nombre(
                            mesure.energie,
                            3
                        );
                }

            }


            // CONTACTEUR

            const contacteur =
                bloc.querySelector(
                    ".compteur-contacteur"
                );


            if (contacteur) {

                if (compteur.contacteur) {

                    contacteur.textContent =
                        "ON";

                    contacteur.classList.remove(
                        "text-red-600"
                    );

                    contacteur.classList.add(
                        "text-green-600"
                    );

                } else {

                    contacteur.textContent =
                        "OFF";

                    contacteur.classList.remove(
                        "text-green-600"
                    );

                    contacteur.classList.add(
                        "text-red-600"
                    );
                }
            }

            // ESP32

            const esp32 =
                bloc.querySelector(
                    ".statut-esp32"
                );


            if (esp32) {

                esp32.classList.remove(
                    "bg-green-100",
                    "text-green-600",
                    "bg-red-100",
                    "text-red-600"
                );


                if (
                    compteur.esp32_connecte === true
                ) {

                    esp32.classList.add(
                        "bg-green-100",
                        "text-green-600"
                    );


                    esp32.setAttribute(
                        "title",
                        "ESP32 connecté"
                    );


                    esp32.setAttribute(
                        "aria-label",
                        "ESP32 connecté"
                    );


                    esp32.innerHTML =
                        '<i data-lucide="wifi" class="w-4 h-4"></i>';

                } else {

                    esp32.classList.add(
                        "bg-red-100",
                        "text-red-600"
                    );


                    esp32.setAttribute(
                        "title",
                        "ESP32 déconnecté"
                    );


                    esp32.setAttribute(
                        "aria-label",
                        "ESP32 déconnecté"
                    );


                    esp32.innerHTML =
                        '<i data-lucide="wifi-off" class="w-4 h-4"></i>';
                }

            }

        });


        // STATISTIQUES DU HAUT

        const nombreCompteurs =
            document.getElementById(
                "nombreCompteurs"
            );


        if (nombreCompteurs) {

            nombreCompteurs.textContent =
                compteurs.length;
        }


        const compteursConnectesElement =
            document.getElementById(
                "compteursConnectes"
            );


        if (compteursConnectesElement) {

            compteursConnectesElement.textContent =
                compteursConnectes;
        }


        const soldeTotalElement =
            document.getElementById(
                "soldeTotal"
            );


        if (soldeTotalElement) {

            soldeTotalElement.textContent =
                nombre(
                    soldeTotal,
                    3
                );
        }


        const soldeGauge =
            document.getElementById(
                "soldeGauge"
            );


        if (soldeGauge) {

            soldeGauge.textContent =
                nombre(
                    soldeTotal,
                    3
                );
        }


        const consommationTotale =
            document.getElementById(
                "consommationTotale"
            );


        if (consommationTotale) {

            consommationTotale.textContent =
                nombre(
                    consommationTotal,
                    3
                );
        }

        // DERNIÈRE MESURE PZEM

        if (compteurs.length > 0) {

            const compteur =
                compteurs[0];


            const mesure =
                compteur.mesure || null;


            if (mesure) {

                // TENSION

                const tension =
                    document.getElementById(
                        "tensionTempsReel"
                    );


                if (tension) {

                    tension.textContent =
                        nombre(
                            mesure.tension,
                            1
                        );
                }


                // COURANT

                const courant =
                    document.getElementById(
                        "courantTempsReel"
                    );


                if (courant) {

                    courant.textContent =
                        nombre(
                            mesure.courant,
                            3
                        );
                }


                // PUISSANCE

                const puissance =
                    document.getElementById(
                        "puissanceTempsReel"
                    );


                if (puissance) {

                    puissance.textContent =
                        nombre(
                            mesure.puissance,
                            1
                        );
                }


                // ÉNERGIE

                const energie =
                    document.getElementById(
                        "energieTempsReel"
                    );


                if (energie) {

                    energie.textContent =
                        nombre(
                            mesure.energie,
                            3
                        );
                }


                // DATE

                const dateMesure =
                    document.getElementById(
                        "dateMesureTempsReel"
                    );


                if (
                    dateMesure &&
                    mesure.date_mesure
                ) {

                    dateMesure.textContent =
                        "Dernière mesure : " +
                        formaterDate(
                            mesure.date_mesure
                        );
                }

                // STATUT PZEM

                const pzemStatut =
                    document.getElementById(
                        "pzemStatut"
                    );


                if (pzemStatut) {

                    pzemStatut.textContent =
                        "● Temps réel";


                    pzemStatut.classList.remove(
                        "text-red-600",
                        "bg-red-50"
                    );


                    pzemStatut.classList.add(
                        "text-green-600",
                        "bg-green-50"
                    );
                }

            }

        }
    }




    // ======================================================
    // DASHBOARD ADMIN
    // ======================================================

    // function mettreAJourDashboardAdmin(statistiques) {

    //     if (!statistiques) {
    //         return;
    //     }


    //     // Nombre clients
    //     actualiserElement(
    //         document.getElementById(
    //             "adminNombreClients"
    //         ),
    //         statistiques.nombre_clients ?? 0
    //     );


    //     // Nombre compteurs
    //     actualiserElement(
    //         document.getElementById(
    //             "adminNombreCompteurs"
    //         ),
    //         statistiques.nombre_compteurs ?? 0
    //     );


    //     // Compteurs connectés
    //     actualiserElement(
    //         document.getElementById(
    //             "adminCompteursConnectes"
    //         ),
    //         statistiques.compteurs_connectes ?? 0
    //     );


    //     // ==================================================
    //     // COMPTEURS COUPÉS
    //     // ==================================================

    //     const compteursCoupes =
    //         Number(
    //             statistiques.compteurs_coupes ?? 0
    //         );

    //     actualiserElement(
    //         document.getElementById(
    //             "adminCompteursCoupes"
    //         ),
    //         compteursCoupes
    //     );


    //     // Solde total
    //     actualiserElement(
    //         document.getElementById(
    //             "adminSoldeTotal"
    //         ),
    //         nombre(
    //             statistiques.solde_total,
    //             3
    //         )
    //     );


    //     // Consommation totale
    //     actualiserElement(
    //         document.getElementById(
    //             "adminConsommationTotale"
    //         ),
    //         nombre(
    //             statistiques.consommation_totale,
    //             3
    //         )
    //     );


    //     // Statut temps réel
    //     afficherStatutTempsReelAdmin(
    //         statistiques
    //     );
    // }



    function mettreAJourDashboardAdminDepuisCompteurs(compteurs) {

        if (!Array.isArray(compteurs)) {
            return;
        }

        let soldeTotal = 0;
        let consommationTotale = 0;
        let compteursConnectes = 0;
        let compteursCoupes = 0;

        compteurs.forEach(function (compteur) {

            soldeTotal += Number(compteur.solde || 0);

            consommationTotale += Number(
                compteur.consommation_totale || 0
            );

            if (Boolean(compteur.esp32_connecte)) {
                compteursConnectes++;
            }

            if (!Boolean(compteur.contacteur)) {
                compteursCoupes++;
            }
        });

        actualiserElement(
            document.getElementById("adminNombreCompteurs"),
            compteurs.length
        );

        actualiserElement(
            document.getElementById("adminCompteursConnectes"),
            compteursConnectes
        );

        actualiserElement(
            document.getElementById("adminCompteursCoupes"),
            compteursCoupes
        );

        actualiserElement(
            document.getElementById("adminSoldeTotal"),
            nombre(soldeTotal, 3)
        );

        actualiserElement(
            document.getElementById("adminConsommationTotale"),
            nombre(consommationTotale, 3)
        );
    }


    // ======================================================
    // STATUT TEMPS RÉEL ADMIN
    // ======================================================

    // function afficherStatutTempsReelAdmin(statistiques) {

    //     const indicateur =
    //         document.getElementById(
    //             "adminTempsReelIndicateur"
    //         );

    //     const texte =
    //         document.getElementById(
    //             "adminTempsReelTexte"
    //         );

    //     if (!indicateur && !texte) {
    //         return;
    //     }


    //     const connectes =
    //         Number(
    //             statistiques.compteurs_connectes ?? 0
    //         );

    //     if (connectes > 0) {

    //         if (indicateur) {

    //             indicateur.classList.remove(
    //                 "bg-red-500"
    //             );

    //             indicateur.classList.add(
    //                 "bg-green-500"
    //             );
    //         }

    //         if (texte) {

    //             texte.textContent =
    //                 "Temps réel actif";
    //         }

    //     } else {

    //         if (indicateur) {

    //             indicateur.classList.remove(
    //                 "bg-green-500"
    //             );

    //             indicateur.classList.add(
    //                 "bg-red-500"
    //             );
    //         }

    //         if (texte) {

    //             texte.textContent =
    //                 "Aucun compteur connecté";
    //         }
    //     }
    // }


    // ======================================================
    // DERNIÈRE ACTUALISATION ADMIN
    // ======================================================

    // function mettreAJourDerniereActualisationAdmin() {

    //     const element =
    //         document.getElementById(
    //             "adminDerniereActualisation"
    //         );

    //     if (!element) {
    //         return;
    //     }

    //     const maintenant = new Date();

    //     element.textContent =
    //         maintenant.toLocaleTimeString(
    //             "fr-FR"
    //         );
    // }


    // ======================================================
    // TABLEAU DES COMPTEURS ADMIN
    // ======================================================

    function mettreAJourTableauAdmin(compteurs) {

        if (!Array.isArray(compteurs)) {
            return;
        }


        compteurs.forEach(function (compteur) {

            const deviceId =
                compteur.device_id;

            if (!deviceId) {
                return;
            }


            const ligne =
                document.querySelector(
                    `.admin-compteur-row[data-device-id="${deviceId}"]`
                );

            if (!ligne) {
                return;
            }

            // SOLDE

            const solde =
                ligne.querySelector(
                    ".admin-compteur-solde"
                );

            if (solde) {

                solde.textContent =
                    nombre(
                        compteur.solde,
                        3
                    );
            }


            // ESP32

            const esp32 =
                ligne.querySelector(
                    ".admin-compteur-esp32"
                );

            const point =
                ligne.querySelector(
                    ".admin-compteur-esp32-point"
                );

            const texte =
                ligne.querySelector(
                    ".admin-compteur-esp32-texte"
                );


            if (compteur.esp32_connecte) {

                if (esp32) {

                    esp32.textContent =
                        "Connecté";
                }

                if (texte) {

                    texte.textContent =
                        "Connecté";
                }

                if (point) {

                    point.classList.remove(
                        "bg-red-500"
                    );

                    point.classList.add(
                        "bg-green-500"
                    );
                }

            } else {

                if (esp32) {

                    esp32.textContent =
                        "Déconnecté";
                }

                if (texte) {

                    texte.textContent =
                        "Déconnecté";
                }

                if (point) {

                    point.classList.remove(
                        "bg-green-500"
                    );

                    point.classList.add(
                        "bg-red-500"
                    );
                }
            }


            // CONTACTEUR

            const contacteur =
                ligne.querySelector(
                    ".admin-compteur-contacteur"
                );

            if (contacteur) {

                if (compteur.contacteur) {

                    contacteur.textContent =
                        "ON";

                    contacteur.classList.remove(
                        "text-red-600"
                    );

                    contacteur.classList.add(
                        "text-green-600"
                    );

                } else {

                    contacteur.textContent =
                        "OFF";

                    contacteur.classList.remove(
                        "text-green-600"
                    );

                    contacteur.classList.add(
                        "text-red-600"
                    );
                }
            }
        });
    }


    // ======================================================
    // GRAPHIQUES TENSION / COURANT / PUISSANCE
    // ======================================================

    function mettreAJourGraphiques(compteurs) {

        if (!Array.isArray(compteurs)) {
            return;
        }

        if (typeof Chart === "undefined") {
            console.warn(
                "Chart.js n'est pas chargé."
            );

            return;
        }


        compteurs.forEach(function (compteur) {

            const mesures =
                Array.isArray(compteur.mesures)
                    ? compteur.mesures
                    : [];


            if (!mesures.length) {
                return;
            }


            const labels = mesures.map(
                function (mesure) {

                    return formaterDate(
                        mesure.date_mesure
                    );
                }
            );


            const tensions = mesures.map(
                function (mesure) {

                    return Number(
                        mesure.tension || 0
                    );
                }
            );


            const courants = mesures.map(
                function (mesure) {

                    return Number(
                        mesure.courant || 0
                    );
                }
            );


            const puissances = mesures.map(
                function (mesure) {

                    return Number(
                        mesure.puissance || 0
                    );
                }
            );

            // TENSION

            const canvasTension =
                document.getElementById(
                    "graphiqueTension"
                );

            if (canvasTension) {

                if (graphiques.tension) {

                    graphiques.tension.destroy();
                }


                const ctx =
                    canvasTension.getContext(
                        "2d"
                    );


                graphiques.tension =
                    new Chart(ctx, {

                        type: "line",

                        data: {

                            labels: labels,

                            datasets: [

                                {
                                    label:
                                        "Tension (V)",

                                    data:
                                        tensions,

                                    borderWidth: 2,

                                    tension: 0.35,

                                    fill: false,

                                    pointRadius: 2
                                }
                            ]
                        },

                        options: {

                            responsive: true,

                            maintainAspectRatio:
                                false,

                            interaction: {

                                mode: "index",

                                intersect: false
                            },

                            scales: {

                                y: {

                                    beginAtZero: false
                                }
                            }
                        }
                    });
            }

            // COURANT

            const canvasCourant =
                document.getElementById(
                    "graphiqueCourant"
                );

            if (canvasCourant) {

                if (graphiques.courant) {

                    graphiques.courant.destroy();
                }


                const ctx =
                    canvasCourant.getContext(
                        "2d"
                    );


                graphiques.courant =
                    new Chart(ctx, {

                        type: "line",

                        data: {

                            labels: labels,

                            datasets: [

                                {
                                    label:
                                        "Courant (A)",

                                    data:
                                        courants,

                                    borderWidth: 2,

                                    tension: 0.35,

                                    fill: false,

                                    pointRadius: 2
                                }
                            ]
                        },

                        options: {

                            responsive: true,

                            maintainAspectRatio:
                                false,

                            interaction: {

                                mode: "index",

                                intersect: false
                            },

                            scales: {

                                y: {

                                    beginAtZero: true
                                }
                            }
                        }
                    });
            }


            // ==============================================
            // PUISSANCE
            // ==============================================

            const canvasPuissance =
                document.getElementById(
                    "graphiquePuissance"
                );

            if (canvasPuissance) {

                if (graphiques.puissance) {

                    graphiques.puissance.destroy();
                }


                const ctx =
                    canvasPuissance.getContext(
                        "2d"
                    );


                graphiques.puissance =
                    new Chart(ctx, {

                        type: "line",

                        data: {

                            labels: labels,

                            datasets: [

                                {
                                    label:
                                        "Puissance (W)",

                                    data:
                                        puissances,

                                    borderWidth: 2,

                                    tension: 0.35,

                                    fill: false,

                                    pointRadius: 2
                                }
                            ]
                        },

                        options: {

                            responsive: true,

                            maintainAspectRatio:
                                false,

                            interaction: {

                                mode: "index",

                                intersect: false
                            },

                            scales: {

                                y: {

                                    beginAtZero: true
                                }
                            }
                        }
                    });
            }

        });
    }


    // ======================================================
    // GRAPHIQUE CONSOMMATION CLIENT
    // ======================================================

    function initialiserGraphiquesConsommation() {

        const blocs =
            document.querySelectorAll(
                ".compteur-consommation"
            );


        if (!blocs.length) {

            return;
        }


        if (typeof Chart === "undefined") {

            console.warn(
                "Chart.js n'est pas chargé pour la consommation."
            );

            return;
        }


        blocs.forEach(function (bloc, index) {

            const canvas =
                bloc.querySelector(
                    ".graphique-consommation"
                );


            if (!canvas) {

                return;
            }


            if (canvas._chartInstance) {

                return;
            }


            const labelsBruts =
                bloc.dataset.labels || "";


            const energiesBrutes =
                bloc.dataset.energies || "";


            const puissancesBrutes =
                bloc.dataset.puissances || "";


            const labels =
                labelsBruts
                    .split(",")
                    .map(
                        value => value.trim()
                    )
                    .filter(
                        value => value !== ""
                    );


            const energies =
                energiesBrutes
                    .split(",")
                    .map(
                        value => Number(value)
                    )
                    .filter(
                        value => !isNaN(value)
                    );


            const puissances =
                puissancesBrutes
                    .split(",")
                    .map(
                        value => Number(value)
                    )
                    .filter(
                        value => !isNaN(value)
                    );


            if (!labels.length) {

                return;
            }


            const ctx =
                canvas.getContext(
                    "2d"
                );


            canvas._chartInstance =
                new Chart(ctx, {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {
                                label:
                                    "Énergie (kWh)",

                                data:
                                    energies,

                                borderWidth: 2,

                                tension: 0.35,

                                fill: false,

                                pointRadius: 3,

                                pointHoverRadius: 5
                            },

                            {
                                label:
                                    "Puissance (W)",

                                data:
                                    puissances,

                                borderWidth: 2,

                                tension: 0.35,

                                fill: false,

                                pointRadius: 3,

                                pointHoverRadius: 5
                            }

                        ]
                    },


                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,


                        interaction: {

                            mode: "index",

                            intersect: false
                        },


                        plugins: {

                            legend: {

                                display: true
                            },


                            tooltip: {

                                enabled: true
                            }
                        },


                        scales: {

                            x: {

                                title: {

                                    display: true,

                                    text: "Date"
                                }
                            },


                            y: {

                                beginAtZero: true,

                                title: {

                                    display: true,

                                    text: "Valeur"
                                }
                            }
                        }
                    }
                });
        });
    }


    // ======================================================
    // MISE À JOUR DU SOLDE SUR CONSOMMATION
    // ======================================================

    function mettreAJourSoldesConsommation(compteurs) {

        const blocs =
            document.querySelectorAll(
                ".compteur-consommation"
            );


        if (!blocs.length) {

            return;
        }


        if (!Array.isArray(compteurs)) {

            return;
        }


        blocs.forEach(function (bloc) {

            const deviceId =
                bloc.dataset.deviceId;


            if (!deviceId) {

                return;
            }


            const compteur =
                compteurs.find(
                    function (item) {

                        return item.device_id === deviceId;
                    }
                );


            if (!compteur) {

                return;
            }


            const soldeElement =
                bloc.querySelector(
                    ".compteur-solde-live"
                );


            if (soldeElement) {

                soldeElement.textContent =
                    nombre(
                        compteur.solde,
                        3
                    );
            }
        });
    }


    // ======================================================
    // STATUT TEMPS RÉEL PAGE CONSOMMATION
    // ======================================================

    function mettreAJourStatutConsommation(compteurs) {

        const statut =
            document.getElementById(
                "tempsReelStatut"
            );


        if (!statut) {

            return;
        }


        if (!Array.isArray(compteurs)) {

            statut.textContent =
                "● Erreur de récupération des données";

            return;
        }


        if (compteurs.length === 0) {

            statut.textContent =
                "● Aucun compteur";

            return;
        }


        const connectes =
            compteurs.filter(
                function (compteur) {

                    return compteur.esp32_connecte === true;
                }
            ).length;


        if (connectes > 0) {

            statut.textContent =
                "● Actualisation automatique — " +
                connectes +
                " compteur(s) connecté(s)";

        } else {

            statut.textContent =
                "● Aucun ESP32 connecté";
        }
    }



    // ======================================================
    // CHARGEMENT TEMPS RÉEL
    // ======================================================

    async function chargerTempsReel() {

        try {
            // DÉTECTION PAGE CLIENT

            const matchClient =
                window.location.pathname.match(
                    /\/admin-dashboard\/clients\/(\d+)\/compteurs\/?/
                );

            let urlAPI = "/api/temps-reel/";

            if (matchClient) {

                const clientId =
                    matchClient[1];

                urlAPI =
                    `/api/admin/clients/${clientId}/compteurs/`;

                console.log(
                    "API client utilisée :",
                    urlAPI
                );
            }

            // APPEL API

            const response =
                await fetch(
                    urlAPI,
                    {
                        method: "GET",

                        headers: {
                            "X-Requested-With":
                                "XMLHttpRequest",

                            "Accept":
                                "application/json"
                        },

                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Erreur HTTP : " +
                    response.status
                );
            }


            const data =
                await response.json();


            console.log(
                "Temps réel :",
                data
            );


            // VÉRIFICATION API

            if (!data.success) {

                console.warn(
                    "API temps réel : success=false"
                );

                return;
            }


            // COMPTEURS

            if (Array.isArray(data.compteurs)) {

                // Dashboard

                mettreAJourDashboard(
                    data.compteurs
                );

                // Consommation

                mettreAJourSoldesConsommation(
                    data.compteurs
                );


                // Statut consommation

                mettreAJourStatutConsommation(
                    data.compteurs
                );

                // Graphiques

                mettreAJourGraphiques(
                    data.compteurs
                );

                // Tableau admin

                mettreAJourTableauAdmin(
                    data.compteurs
                );

                // Statistiques admin

                mettreAJourDashboardAdminDepuisCompteurs(
                    data.compteurs
                );
            }


        } catch (error) {

            console.error(
                "Erreur actualisation temps réel :",
                error
            );


            // STATUT TEMPS RÉEL

            const statut =
                document.getElementById(
                    "tempsReelStatut"
                );


            if (statut) {

                statut.textContent =
                    "● Connexion au serveur impossible";
            }

            // TEXTE ADMIN

            const texteAdmin =
                document.getElementById(
                    "adminTempsReelTexte"
                );


            if (texteAdmin) {

                texteAdmin.textContent =
                    "Connexion impossible";
            }

            // INDICATEUR ADMIN
            const indicateurAdmin =
                document.getElementById(
                    "adminTempsReelIndicateur"
                );


            if (indicateurAdmin) {

                indicateurAdmin.classList.remove(
                    "bg-green-500"
                );

                indicateurAdmin.classList.add(
                    "bg-red-500"
                );
            }
        }
    }




    // ======================================================
    // INITIALISATION
    // ======================================================

    initialiserGraphiquesConsommation();

    // Première récupération immédiatement
    chargerTempsReel();

    // Actualisation toutes les 5 secondes
    setInterval(
        chargerTempsReel,
        1000
    );


});

