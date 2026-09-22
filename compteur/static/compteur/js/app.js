
document.addEventListener("DOMContentLoaded", function () {


    // ============================================================
    // LUCIDE
    // ============================================================

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }


    // ============================================================
    // MENU MOBILE
    // ============================================================

    const menuButton =
        document.getElementById("menuButton");

    const sidebar =
        document.getElementById("sidebar");

    const overlay =
        document.getElementById("sidebarOverlay");


    function openSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.remove(
            "-translate-x-full"
        );

        if (overlay) {
            overlay.classList.remove("hidden");
        }
    }


    function closeSidebar() {

        if (!sidebar) {
            return;
        }

        sidebar.classList.add(
            "-translate-x-full"
        );

        if (overlay) {
            overlay.classList.add("hidden");
        }
    }


    if (menuButton) {

        menuButton.addEventListener(
            "click",
            openSidebar
        );

    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeSidebar
        );

    }


    document
        .querySelectorAll("#sidebar a")
        .forEach(function (link) {

            link.addEventListener(
                "click",
                function () {

                    if (window.innerWidth < 1024) {
                        closeSidebar();
                    }

                }
            );

        });


    // ============================================================
    // GRAPHIQUES
    // ============================================================

    const graphiques = {};


    function creerGraphique(bloc) {

        const canvas =
            bloc.querySelector(
                ".graphique-consommation"
            );


        if (!canvas) {
            return null;
        }


        const labelsTexte =
            bloc.dataset.labels || "";


        const energiesTexte =
            bloc.dataset.energies || "";


        const puissancesTexte =
            bloc.dataset.puissances || "";


        const labels =
            labelsTexte
                ? labelsTexte.split(",")
                : [];


        const energies =
            energiesTexte
                ? energiesTexte
                    .split(",")
                    .map(Number)
                : [];


        const puissances =
            puissancesTexte
                ? puissancesTexte
                    .split(",")
                    .map(Number)
                : [];


        if (
            typeof Chart === "undefined"
        ) {

            console.error(
                "Chart.js n'est pas chargé."
            );

            return null;
        }


        const graphique =
            new Chart(canvas, {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label: "Énergie (kWh)",

                            data: energies,

                            borderWidth: 3,

                            tension: 0.3,

                            fill: false,

                            pointRadius: 4,

                            pointHoverRadius: 6
                        },


                        {
                            label: "Puissance (W)",

                            data: puissances,

                            borderWidth: 3,

                            tension: 0.3,

                            fill: false,

                            pointRadius: 4,

                            pointHoverRadius: 6
                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    animation: false,

                    interaction: {

                        mode: "index",

                        intersect: false

                    },


                    plugins: {

                        legend: {

                            position: "top"

                        },

                        tooltip: {

                            mode: "index",

                            intersect: false

                        }

                    },


                    scales: {

                        x: {

                            title: {

                                display: true,

                                text: "Heure"

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


        return graphique;
    }


    // ============================================================
    // INITIALISER LES GRAPHIQUES
    // ============================================================

    document
        .querySelectorAll(
            ".compteur-consommation"
        )
        .forEach(function (bloc) {

            const deviceId =
                bloc.dataset.deviceId;


            const graphique =
                creerGraphique(bloc);


            if (graphique) {

                graphiques[deviceId] =
                    graphique;

            }

        });


    // ============================================================
    // FORMATAGE
    // ============================================================

    function nombre(valeur, decimales) {

        if (
            valeur === null ||
            valeur === undefined ||
            isNaN(valeur)
        ) {
            return "0";
        }


        return Number(valeur)
            .toFixed(decimales);
    }


    // ============================================================
    // FORMAT DATE
    // ============================================================

    function formaterDate(dateISO) {

        if (!dateISO) {
            return "-";
        }


        const date =
            new Date(dateISO);


        if (isNaN(date.getTime())) {
            return "-";
        }


        return date.toLocaleString(
            "fr-FR",
            {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            }
        );
    }


    // ============================================================
    // MISE À JOUR DASHBOARD
    // ============================================================

    function mettreAJourDashboard(
        compteurs
    ) {

        if (!compteurs.length) {
            return;
        }


        let nombreCompteurs =
            compteurs.length;


        let connectes = 0;

        let soldeTotal = 0;

        let consommationTotale = 0;


        compteurs.forEach(function (compteur) {

            if (compteur.esp32_connecte) {
                connectes++;
            }


            soldeTotal +=
                Number(compteur.solde || 0);


            consommationTotale +=
                Number(
                    compteur.consommation_totale || 0
                );

        });


        // --------------------------------------------------------
        // STATISTIQUES
        // --------------------------------------------------------

        const nombreElement =
            document.getElementById(
                "nombreCompteurs"
            );


        const connectesElement =
            document.getElementById(
                "compteursConnectes"
            );


        const soldeElement =
            document.getElementById(
                "soldeTotal"
            );


        const consommationElement =
            document.getElementById(
                "consommationTotale"
            );


        if (nombreElement) {

            nombreElement.textContent =
                nombreCompteurs;

        }


        if (connectesElement) {

            connectesElement.textContent =
                connectes;

        }


        if (soldeElement) {

            soldeElement.textContent =
                nombre(
                    soldeTotal,
                    3
                );

        }


        if (consommationElement) {

            consommationElement.textContent =
                nombre(
                    consommationTotale,
                    3
                );

        }


        // --------------------------------------------------------
        // SOLDE JAUGE
        // --------------------------------------------------------

        const gauge =
            document.getElementById(
                "soldeGauge"
            );


        if (gauge) {

            gauge.textContent =
                nombre(
                    soldeTotal,
                    3
                );

        }


        // --------------------------------------------------------
        // TROUVER LA MESURE LA PLUS RÉCENTE
        // --------------------------------------------------------

        let derniere =
            null;


        compteurs.forEach(function (compteur) {

            if (!compteur.mesure) {
                return;
            }


            const date =
                new Date(
                    compteur.mesure.date_mesure
                );


            if (
                !derniere ||
                date >
                derniere.date
            ) {

                derniere = {

                    date: date,

                    mesure:
                        compteur.mesure

                };

            }

        });


        if (derniere) {

            const mesure =
                derniere.mesure;


            const tension =
                document.getElementById(
                    "tensionTempsReel"
                );


            const courant =
                document.getElementById(
                    "courantTempsReel"
                );


            const puissance =
                document.getElementById(
                    "puissanceTempsReel"
                );


            const energie =
                document.getElementById(
                    "energieTempsReel"
                );


            const dateMesure =
                document.getElementById(
                    "dateMesureTempsReel"
                );


            if (tension) {

                tension.textContent =
                    nombre(
                        mesure.tension,
                        2
                    );

            }


            if (courant) {

                courant.textContent =
                    nombre(
                        mesure.courant,
                        3
                    );

            }


            if (puissance) {

                puissance.textContent =
                    nombre(
                        mesure.puissance,
                        2
                    );

            }


            if (energie) {

                energie.textContent =
                    nombre(
                        mesure.energie,
                        3
                    );

            }


            if (dateMesure) {

                dateMesure.textContent =
                    "Dernière mesure : " +
                    formaterDate(
                        mesure.date_mesure
                    );

            }

        }


        // --------------------------------------------------------
        // CARTES DES COMPTEURS
        // --------------------------------------------------------

        compteurs.forEach(function (compteur) {

            const carte =
                document.querySelector(
                    '.compteur-card-temps-reel[data-device-id="' +
                    compteur.device_id +
                    '"]'
                );


            if (!carte) {
                return;
            }


            const solde =
                carte.querySelector(
                    ".compteur-solde"
                );


            const contacteur =
                carte.querySelector(
                    ".compteur-contacteur"
                );


            const puissance =
                carte.querySelector(
                    ".compteur-puissance"
                );


            const energie =
                carte.querySelector(
                    ".compteur-energie"
                );


            const statut =
                carte.querySelector(
                    ".statut-esp32"
                );


            if (solde) {

                solde.textContent =
                    nombre(
                        compteur.solde,
                        3
                    );

            }


            if (contacteur) {

                contacteur.textContent =
                    compteur.contacteur
                        ? "ON"
                        : "OFF";

            }


            if (
                puissance &&
                compteur.mesure
            ) {

                puissance.textContent =
                    nombre(
                        compteur.mesure.puissance,
                        2
                    );

            }


            if (
                energie &&
                compteur.mesure
            ) {

                energie.textContent =
                    nombre(
                        compteur.mesure.energie,
                        3
                    );

            }


            if (statut) {

                if (
                    compteur.esp32_connecte
                ) {

                    statut.textContent =
                        "● Connecté";

                    statut.className =
                        "statut-esp32 " +
                        "text-green-600 " +
                        "bg-green-50 " +
                        "px-2 py-1 rounded-full " +
                        "text-xs";

                } else {

                    statut.textContent =
                        "● Déconnecté";

                    statut.className =
                        "statut-esp32 " +
                        "text-red-600 " +
                        "bg-red-50 " +
                        "px-2 py-1 rounded-full " +
                        "text-xs";

                }

            }

        });

    }


    // ============================================================
    // MISE À JOUR DES COURBES
    // ============================================================

    function mettreAJourGraphiques(
        compteurs
    ) {

        compteurs.forEach(function (compteur) {

            const graphique =
                graphiques[
                    compteur.device_id
                ];


            if (!graphique) {
                return;
            }


            if (
                !compteur.mesures ||
                !compteur.mesures.length
            ) {
                return;
            }


            const labels = [];

            const energies = [];

            const puissances = [];


            compteur.mesures.forEach(
                function (mesure) {

                    labels.push(
                        mesure.heure
                    );


                    energies.push(
                        Number(
                            mesure.energie
                        )
                    );


                    puissances.push(
                        Number(
                            mesure.puissance
                        )
                    );

                }
            );


            graphique.data.labels =
                labels;


            graphique.data.datasets[0].data =
                energies;


            graphique.data.datasets[1].data =
                puissances;


            graphique.update(
                "none"
            );

        });

    }


    // ============================================================
    // API TEMPS RÉEL
    // ============================================================

    let chargementEnCours = false;


    async function chargerTempsReel() {

        if (chargementEnCours) {
            return;
        }


        chargementEnCours = true;


        try {

            const reponse =
                await fetch(
                    "/api/temps-reel/",
                    {
                        method: "GET",

                        cache: "no-store",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            if (!reponse.ok) {

                throw new Error(
                    "Erreur HTTP " +
                    reponse.status
                );

            }


            const data =
                await reponse.json();


            if (
                !data.success ||
                !Array.isArray(
                    data.compteurs
                )
            ) {

                throw new Error(
                    "Réponse API invalide."
                );

            }


            // Dashboard

            mettreAJourDashboard(
                data.compteurs
            );


            // Graphiques

            mettreAJourGraphiques(
                data.compteurs
            );


            // ----------------------------------------------------
            // STATUT TEMPS RÉEL
            // ----------------------------------------------------

            const statut =
                document.getElementById(
                    "tempsReelStatut"
                );


            if (statut) {

                statut.textContent =
                    "● Données actualisées à " +
                    new Date().toLocaleTimeString(
                        "fr-FR"
                    );

                statut.className =
                    "text-xs text-green-600 mt-2";

            }


        } catch (erreur) {

            console.error(
                "Erreur temps réel :",
                erreur
            );


            const statut =
                document.getElementById(
                    "tempsReelStatut"
                );


            if (statut) {

                statut.textContent =
                    "● Connexion au serveur interrompue";

                statut.className =
                    "text-xs text-red-600 mt-2";

            }

        } finally {

            chargementEnCours =
                false;

        }

    }


    // ============================================================
    // PREMIER CHARGEMENT
    // ============================================================

    chargerTempsReel();


    // ============================================================
    // ACTUALISATION AUTOMATIQUE
    // ============================================================

    setInterval(
        chargerTempsReel,
        5000
    );

});

