from django.core.management.base import BaseCommand
from principal.models import Compet, CompetExtra
import shutil
import os
from django.conf import settings
from collections import defaultdict
from principal.utils.utils import capitalize_name

class Command(BaseCommand):
    help = "Generate HTML rankings by state for a given compet_type."

    def add_arguments(self, parser):
        parser.add_argument("compet_type", type=int, help="Compet type (int)")
        parser.add_argument(
            "--output-dir",
            type=str,
            default=os.path.join(settings.BASE_DIR, "rankings"),
            help="Directory where HTML files will be saved",
        )

    def handle(self, *args, **options):
        compet_type = options["compet_type"]
        output_dir = options["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        compets = (
            Compet.objects.select_related("compet_school")
            .filter(compet_type=compet_type, compet_points_fase2__gte=1)
            .order_by("compet_school__school_state", "-compet_points_fase2", "compet_name")
        )

        compets_extra = CompetExtra.objects.filter(compet__compet_type=compet_type)
        compets_extra.update(compet_state_rank_fase2=None)
        compets_by_state = defaultdict(list)
        for c in compets:
            compets_by_state[c.compet_school.school_state].append(c)


        level = compet_type
        if compet_type == 7:
            level = "Júnior"
            compet_type_txt = 'ij'
        elif compet_type == 1:
            compet_type_txt = 'i1'
        elif compet_type == 2:
            compet_type_txt = 'i2'
        else:
            print("bad compet_type", compet_type, file=sys.stderr)
            sys.exit(-1)
            
        index_links = []  # collect links for index.html

        total_medals = {}

        index_dir = os.path.join(output_dir, compet_type_txt)
        try:
            shutil.rmtree(index_dir)
        except:
            pass
        os.mkdir(index_dir)

        
        for state, state_compets in compets_by_state.items():
            total_medals[state] = 0
            ranked = []
            rank = 0
            prev_points = None
            count = 0
            for c in state_compets:
                count += 1
                if c.compet_points_fase2 != prev_points:
                    rank = count
                ranked.append((rank, c))
                prev_points = c.compet_points_fase2

            half_n = (len(ranked) + 1) // 2
            ranked = ranked[:half_n]

            html = [
                f"title: Honra ao Mérito Estadual - {state} - OBI2025 - Modalidade Iniciação Nível {level}",
                "template:flatpages_result.html",
                "",
                "",
                "",
                '<table class="table table-sm table-striped table-bordered">',
                '<thead class="table-primary">', 
                '<tr>',
                '<td align="center">Classif.</td>',
                '<td align="center">Nota<sup>1</sup}</td>',
                '<td>Nome</td>',
                '<td>Escola</td>',
                '<td>Cidade</td>',
                '</thead>',
            ]

            for rank, c in ranked:
                if c.compet_points_fase2<10:
                    break
                nota = 500*c.compet_points_fase2/20

                try:
                    c_extra = compets_extra.get(compet_id=c.compet_id)
                except:
                    print("does not exist", c.compet_id_full)
                    c_extra = CompetExtra(compet_id=c.compet_id)
                c_extra.compet_state_rank_fase2 = rank
                c_extra.save()
                total_medals[c.compet_school.school_state] += 1
                html.append(
                    "<tr>"
                    f"<td>{rank}</td>"
                    f"<td>{nota:.1f}</td>"
                    f"<td>{c.compet_name}</td>"
                    f"<td>{capitalize_name(c.compet_school.school_name)}</td>"
                    f"<td>{capitalize_name(c.compet_school.school_city)}/{c.compet_school.school_state}</td>"
                    "</tr>"
                )

            html.append("</table>")
            obs = '''<p>1. Observação: A Nota mostrada é equivalente à pontuação obtida
na Fase 2 (a Nota é simplesmente a pontuação normalizada para o valor máximo de 500 pontos, para permitir
comparação com anos anteriores).</p>'''
            html.append(obs)

            filename = f"{state}_{compet_type_txt}"
            filepath = os.path.join(index_dir, filename)+".html"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(html))

            index_links.append((state, filename))
            self.stdout.write(self.style.SUCCESS(f"Generated {filepath}"))

        # Build index.html
        index_html = [
            f"title: Honra ao Mérito Estadual - OBI2025 - Modalidade Iniciação Nível {level}",
            "template:flatpages_result.html",
            "<ul>",
        ]
        for state, filename in sorted(index_links):
            index_html.append(f'<li><a href="{filename}">{state}</a></li>')
        index_html.append("</ul>")


        index_path = os.path.join(output_dir, f"{compet_type_txt}.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_html))

        total = 0
        for i in total_medals.keys():
            total += total_medals[i]
        self.stdout.write(self.style.SUCCESS(f"Medals: {total}"))
        self.stdout.write(self.style.SUCCESS(f"Medals/state: {total_medals}"))
        self.stdout.write(self.style.SUCCESS(f"Generated index file at {index_path}"))
