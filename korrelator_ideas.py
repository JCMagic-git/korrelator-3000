import argparse
import json
from datetime import datetime
from pathlib import Path

# Pfad zur Ideendatei
DATA_DIR = Path(__file__).parent / "data"
IDEAS_FILE = DATA_DIR / "ideas.json"


def ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not IDEAS_FILE.exists():
        IDEAS_FILE.write_text("[]", encoding="utf-8")


def load_ideas():
    ensure_data_file()
    try:
        return json.loads(IDEAS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # Fallback, falls Datei mal korrupt ist
        return []


def save_ideas(ideas):
    IDEAS_FILE.write_text(json.dumps(ideas, indent=2, ensure_ascii=False), encoding="utf-8")


def get_next_id(ideas):
    if not ideas:
        return 1
    return max(idea["id"] for idea in ideas) + 1

def cmd_delete(args):
    ideas = load_ideas()
    new_ideas = [i for i in ideas if i["id"] != args.id]

    if len(new_ideas) == len(ideas):
        print(f"Keine Idee mit ID {args.id} gefunden.")
        return

    save_ideas(new_ideas)
    print(f"Idee #{args.id} wurde gelöscht.")

def cmd_add(args):
    ideas = load_ideas()
    idea = {
        "id": get_next_id(ideas),
        "title": args.title,
        "category": args.category or "",
        "notes": args.notes or "",
        "status": "idea",  # idea | planned | implemented (kannst du später erweitern)
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    ideas.append(idea)
    save_ideas(ideas)
    print(f"Idee #{idea['id']} hinzugefügt:")
    print(f"  Titel    : {idea['title']}")
    if idea["category"]:
        print(f"  Kategorie: {idea['category']}")
    if idea["notes"]:
        print(f"  Notizen  : {idea['notes']}")


def cmd_list(args):
    ideas = load_ideas()
    if not ideas:
        print("Noch keine Ideen gespeichert.")
        return

    # Optional nach Status oder Kategorie filtern
    filtered = ideas
    if args.status:
        filtered = [i for i in filtered if i.get("status") == args.status]
    if args.category:
        filtered = [i for i in filtered if i.get("category") == args.category]

    if not filtered:
        print("Keine passenden Ideen gefunden.")
        return

    for idea in filtered:
        print(f"#{idea['id']}: {idea['title']}")
        if idea.get("category"):
            print(f"   Kategorie: {idea['category']}")
        print(f"   Status   : {idea.get('status', 'idea')}")
        print(f"   Erstellt : {idea.get('created_at', '-')}")
        if idea.get("notes"):
            print(f"   Notizen  : {idea['notes']}")
        print("-" * 40)


def cmd_update_status(args):
    ideas = load_ideas()
    for idea in ideas:
        if idea["id"] == args.id:
            idea["status"] = args.status
            save_ideas(ideas)
            print(f"Status von Idee #{args.id} auf '{args.status}' gesetzt.")
            return
    print(f"Keine Idee mit ID {args.id} gefunden.")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Verwalte Datenfeld-Ideen für den Korrelator 3000."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Neue Idee hinzufügen")
    p_add.add_argument("title", help="Titel der Idee (z. B. 'Schwimmbäder pro 100.000 Einwohner')")
    p_add.add_argument("-c", "--category", help="Kategorie (z. B. Infrastruktur, Gesundheit, Verkehr)")
    p_add.add_argument("-n", "--notes", help="Optionale Notizen / Datenquelle")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="Ideen auflisten")
    p_list.add_argument("-s", "--status", help="Nach Status filtern (idea, planned, implemented)")
    p_list.add_argument("-c", "--category", help="Nach Kategorie filtern")
    p_list.set_defaults(func=cmd_list)

    # update-status
    p_status = subparsers.add_parser("status", help="Status einer Idee ändern")
    p_status.add_argument("id", type=int, help="ID der Idee")
    p_status.add_argument("status", choices=["idea", "planned", "implemented"], help="Neuer Status")
    p_status.set_defaults(func=cmd_update_status)

    # delete
    p_delete = subparsers.add_parser("delete", help="Idee löschen")
    p_delete.add_argument("id", type=int, help="ID der zu löschenden Idee")
    p_delete.set_defaults(func=cmd_delete)


    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()


