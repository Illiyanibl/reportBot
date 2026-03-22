import logging
class MainReport:
    def __init__(self):
        logging.basicConfig(
            filename="report.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s"
        )

    @staticmethod
    def start(login: str, password: str, start_year: str, end_year: str, start_month: str, end_month: str, url: str, action: str = 'create_json'):
        main_report = MainReport()
        logging.info(f"Команда start успешна start_year {start_year}, end_year {end_year}")
        match action:
            case "create_json":
                pass
            case "create_exel":
                main_report.build_excel_report()
            case _:
                print("Unknown command")