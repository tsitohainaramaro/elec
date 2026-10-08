import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Compteur, Mesure


class Esp32ApiTests(TestCase):
    def setUp(self):
        self.compteur = Compteur.objects.create(
            utilisateur=User.objects.create_user(username="esp32-test"),
            device_id="COMPTEUR_01",
            solde=Decimal("5.000"),
        )

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_pzem_measurement_accepts_firmware_payload_and_keeps_response_fields(self):
        response = self.post_json(
            reverse("compteur:api_pzem_mesure"),
            {
                "device_id": "COMPTEUR_01",
                "tension": 220.5,
                "courant": 1.25,
                "puissance": 275.6,
                "energie": 2.0,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertIn("solde", body)
        self.assertIn("contacteur", body)
        self.assertEqual(Mesure.objects.count(), 1)

    def test_pzem_consumption_updates_balance(self):
        self.post_json(
            reverse("compteur:api_pzem_mesure"),
            {
                "device_id": "COMPTEUR_01",
                "tension": 220,
                "courant": 1,
                "puissance": 220,
                "energie": 1,
            },
        )
        response = self.post_json(
            reverse("compteur:api_pzem_mesure"),
            {
                "device_id": "COMPTEUR_01",
                "tension": 220,
                "courant": 1,
                "puissance": 220,
                "energie": 3,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["consommation"], 2.0)
        self.compteur.refresh_from_db()
        self.assertEqual(self.compteur.solde, Decimal("3.000"))

    def test_invalid_measurement_returns_readable_error_without_saving(self):
        response = self.post_json(
            reverse("compteur:api_pzem_mesure"),
            {
                "device_id": "COMPTEUR_01",
                "tension": 220,
                "courant": 1,
                "puissance": 220,
                "energie": "NaN",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["error"]["code"], "invalid_measurement")
        self.assertFalse(response.json()["error"]["retryable"])
        self.assertEqual(Mesure.objects.count(), 0)

    def test_invalid_json_has_consistent_error_envelope(self):
        response = self.client.post(
            reverse("compteur:api_esp32_heartbeat"),
            data="{",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_json")

    def test_state_route_keeps_fields_required_by_firmware(self):
        response = self.client.get(
            reverse(
                "compteur:api_esp32_etat",
                kwargs={"device_id": "COMPTEUR_01"},
            )
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertIn("solde", body)
        self.assertIn("autorisation", body)
        self.assertIn("contacteur", body)

    def test_heartbeat_accepts_boolean_and_enforces_authorization(self):
        self.compteur.autorisation = False
        self.compteur.save(update_fields=["autorisation"])

        response = self.post_json(
            reverse("compteur:api_esp32_heartbeat"),
            {"device_id": "COMPTEUR_01", "relais_on": True},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["relais_on"])
        self.compteur.refresh_from_db()
        self.assertFalse(self.compteur.contacteur)
        self.assertTrue(self.compteur.esp32_connecte)

    def test_heartbeat_rejects_string_instead_of_json_boolean(self):
        response = self.post_json(
            reverse("compteur:api_esp32_heartbeat"),
            {"device_id": "COMPTEUR_01", "relais_on": "false"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_relay_state",
        )
