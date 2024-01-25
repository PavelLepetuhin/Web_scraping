import requests
from bs4 import BeautifulSoup
import json
import fake_headers
from pprint import pprint
import  re


def gen_headers():
    headers_gen = fake_headers.Headers(os="win", browser="chrome")
    return headers_gen.generate()


main_response = requests.get("https://hh.ru/search/vacancy?area=1&area=2&hhtmFrom=main&hhtmFromLabel"
                             "=vacancy_search_line&search_field=name&search_field=company_name&search_field"
                             "=description&enable_snippets=false&L_save_area=true&text=Python", headers=gen_headers())
# main_response = requests.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2")
main_html_data = main_response.text
main_soup = BeautifulSoup(main_html_data, "lxml")


vacancy_list_tag = main_soup.find('main', class_="vacancy-serp-content")
parsed_vacancies = []
parsed_vacancies_USD = []

for vacancy_tag in vacancy_list_tag.find_all('div', class_="serp-item"):
    h3_tag = vacancy_tag.find('h3', class_="bloko-header-section-3")
    a_tag = h3_tag.find('a', class_="bloko-link")

    header = h3_tag.text.strip()
    link_relation = a_tag['href']
    # link_absolute = f"https://hh.ru{link_relation}"

    vacancy_response = requests.get(link_relation, headers=gen_headers())
    vacancy_html_data = vacancy_response.text
    vacancy_soup = BeautifulSoup(vacancy_html_data, "lxml")
    vacancy_tag = vacancy_soup.find('div', id="HH-React-Root")
    vacancy_text = vacancy_tag.text.strip()
    vacancy_gross = vacancy_soup.find('span', {"data-qa":"vacancy-salary-compensation-type-gross"})
    if vacancy_gross == None:
        vacancy_gross = vacancy_soup.find('span', {"data-qa":"vacancy-salary-compensation-type-net"})
    # print(type(vacancy_tag))
    # print(type(vacancy_gross))
    if vacancy_gross is None:
        vacancy_gross = "Не указана!"
    else:
        vacancy_gross_text = vacancy_gross.text.strip()
        pattern = r'\xa0'
        sub_pattern = r' '
        vacancy_gross = re.sub(pattern, sub_pattern, vacancy_gross_text)
    # print(vacancy_gross)

    vacancy_company_text = vacancy_soup.find('span', {"data-qa":"bloko-header-2"}).text.strip()
    if vacancy_company_text == None:
        vacancy_company = "Не указана!"
    else:
        vacancy_company = re.sub(r'\xa0', " ", vacancy_company_text)
    vacancy_city = vacancy_soup.find('p', {"data-qa":"vacancy-view-location"})
    if vacancy_city == None:
        vacancy_city = "Город не указан!"
    else:
        vacancy_city = vacancy_city.text.strip()

    pattern = r"([f, F]lask)|([d, D]jango)"
    django_flask = re.findall(pattern, vacancy_text)
    if django_flask != []:
        parsed_vacancies.append({
            "header": header,
            "link": link_relation,
            "gross": vacancy_gross,
            "company": vacancy_company,
            "city": vacancy_city
        })

    pattern_USD = r'\$|\€'
    vacancy_USD = re.findall(pattern_USD, vacancy_gross)
    if vacancy_USD != []:
        parsed_vacancies_USD.append({
            "header": header,
            "link": link_relation,
            "gross": vacancy_gross,
            "company": vacancy_company,
            "city": vacancy_city
        })
    # print(vacancy_USD)


with open("vacancies.json", "w", encoding="utf-8") as f:
    json.dump(parsed_vacancies, f, ensure_ascii=False, indent=4)

with open("vacancies_usd.json", "w", encoding="utf-8") as g:
    json.dump(parsed_vacancies_USD, g, ensure_ascii=False, indent=4)

# pprint(parsed_vacancies)
# print()
# print("-------------------------------------------")
# print()
# pprint(parsed_vacancies_USD)