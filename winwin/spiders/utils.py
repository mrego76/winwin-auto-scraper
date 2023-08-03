# utils.py

# Constants for data types
INTEGER_DATA = (
    "pd_no",
    "pd_delivery_box",
    "pd_cost_price_",
    "pd_sijung_price_basic_",
    "pd_sobija_pan_basic_",
    "pd_dealer_pan_lv1_basic_",
    "pd_dealer_pan_lv2_basic_",
    "pd_dealer_pan_lv3_basic_",
    "pd_gidoga_basic_",
    "pd_margin_so_c_basic_",
    "pd_margin_de_m1_basic_",
    "pd_margin_de_m2_basic_",
    "pd_margin_de_m3_basic_",
    "pd_gidoga_m_basic_",
    "pd_mileage_so_basic_",
    "pd_mileage_dlv1_basic_",
    "pd_mileage_dlv2_basic_",
    "pd_mileage_dlv3_basic_",
    "pd_mileage_gi_basic_",
    "pd_suggest_basic_",
    "pd_delivery_price_basic_",
    "pd_delivery_chack_price_basic_",
)
DECIMAL_DATA = (
    "pd_sobija_margin_basic_",
    "pd_dealer_halin_lv1_basic_",
    "pd_dealer_halin_lv2_basic_",
    "pd_dealer_halin_lv3_basic_",
)


def process_tag(tag, data_dict):
    tag_name = tag.xpath("name()").get()
    name = tag.xpath("@name").get()
    if tag_name == "input" or tag_name == "textarea":
        value = (
            tag.xpath("@value").get()
            if tag_name == "input"
            else tag.xpath("text()").get()
        )
    elif tag_name == "select":
        value = tag.xpath("option[@selected]/@value").get()
    if value is None:
        return
    elif value in ["Y", "checked"] and tag.xpath("@checked").get() is None:
        return
    elif name.startswith(INTEGER_DATA):
        value = int(value.replace(",", ""))
    elif name.startswith(DECIMAL_DATA):
        value = float(value)
    data_dict[name] = value


def extract_winwin_info(table):
    """Extracts name and value from the given table."""
    data_dict = {}
    tags = table.xpath(".//input | .//textarea | .//select")

    for tag in tags:
        process_tag(tag, data_dict)

    return data_dict


def extract_danawa_info(table):
    """Extracts Danawa information from the given table."""
    data_dict = {}
    try:
        first_price = table.xpath('.//a[contains(@href, "일등가")]/text()').get()
        first_price = int(
            first_price[3 : first_price.find("(")].replace(",", "")
        )
        second_price = table.xpath('.//a[contains(@href, "이등가")]/text()').get()
        second_price = int(
            second_price[3 : second_price.find("(")].replace(",", "")
        )
        grade = (
            table.xpath(".//table//p/text()").getall()[4].split("/")[1].strip()
        )
        rank = grade[: grade.find("위")]
        if rank:
            rank = int(rank)
        else:
            rank = 0
        company_count = int(grade[grade.find("(") + 1 : grade.find("개")])
        data_dict = {
            "일등가": first_price,
            "이등가": second_price,
            "순위": rank,
            "업체수": company_count,
        }
    except AttributeError:
        data_dict = {"일등가": 0, "이등가": 0, "순위": 0, "업체수": 0}

    except Exception as e:
        print("#" * 50)
        print(first_price)
        print(second_price)
        print(rank)
        print(company_count)
        print(f"Error occurred while extracting Danawa info: {e}")

    return data_dict


def modify_price(winwin_data, danawa_data, subtract_price):
    """Modifies the price based on the given data."""
    data_dict = {}
    for key, value in winwin_data.items():
        if key.startswith("pd_sobija_pan_basic_"):
            consumer_price = value
    if consumer_price > danawa_data["일등가"]:
        consumer_price = danawa_data["일등가"]
    data_dict["소비자가"] = consumer_price
    return data_dict
