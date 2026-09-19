async def main():

    print("========================================")
    print("   SNMP NETWORK COLLECTOR")
    print("========================================")
    print("Device :", DEVICE_NAME)
    print("IP     :", DEVICE_IP)
    print("Interval:", POLL_INTERVAL, "seconds")
    print()

    initialize_csv()

    snmp_engine = SnmpEngine()   # <-- créé UNE FOIS, réutilisé pour tout le run

    previous_snapshot = None
    previous_time = None

    while True:

        try:
            current_snapshot = await collect_snapshot(snmp_engine)
            current_time = datetime.now()

            # Première mesure
            if previous_snapshot is None:

                print(
                    "[",
                    current_time.strftime("%H:%M:%S"),
                    "] Première mesure reçue."
                )

                previous_snapshot = current_snapshot
                previous_time = current_time

            else:

                elapsed = (
                    current_time - previous_time
                ).total_seconds()

                print(
                    "[",
                    current_time.strftime("%H:%M:%S"),
                    "] Collecte..."
                )

                for index, current in current_snapshot.items():

                    previous = previous_snapshot.get(index)

                    if previous is None:
                        continue

                    # Si les compteurs ne sont pas disponibles
                    if (
                        current["in_octets"] is None
                        or current["out_octets"] is None
                        or previous["in_octets"] is None
                        or previous["out_octets"] is None
                    ):
                        continue

                    # Différence des compteurs
                    in_delta = (
                        current["in_octets"]
                        - previous["in_octets"]
                    )

                    out_delta = (
                        current["out_octets"]
                        - previous["out_octets"]
                    )

                    # Protection contre reset compteur
                    if in_delta < 0:
                        in_delta = 0

                    if out_delta < 0:
                        out_delta = 0

                    # Conversion en Mbps
                    in_mbps = (
                        in_delta * 8
                        / elapsed
                        / 1_000_000
                    )

                    out_mbps = (
                        out_delta * 8
                        / elapsed
                        / 1_000_000
                    )

                    status = current["status"]

                    # Ecriture CSV
                    write_csv_row(
                        current_time.isoformat(
                            timespec="seconds"
                        ),
                        current["interface"],
                        status,
                        in_mbps,
                        out_mbps
                    )

                    print(
                        f"  {current['interface']:18}"
                        f" {status:8}"
                        f" IN={in_mbps:.3f} Mbps"
                        f" OUT={out_mbps:.3f} Mbps"
                    )

                previous_snapshot = current_snapshot
                previous_time = current_time

        except Exception as error:

            print("Collector error:", error)

        await asyncio.sleep(POLL_INTERVAL)


# ==================================================
# START
# ==================================================

if __name__ == "__main__":
    asyncio.run(main())