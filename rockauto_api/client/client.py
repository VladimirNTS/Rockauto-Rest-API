"""Main RockAuto API client implementation."""

import re
import json
import urllib.parse
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from bs4 import BeautifulSoup

from ..models import (
    AccountActivityResult,
    BillingInfo,
    CacheConfiguration,
    Engine,
    ExternalOrderRequest,
    ManufacturerOptions,
    OrderHistoryFilter,
    OrderHistoryItem,
    OrderHistoryResult,
    OrderItem,
    OrderListRequest,
    OrderLookupRequest,
    OrderStatus,
    OrderStatusError,
    OrderStatusResult,
    PartCache,
    PartCategory,
    PartGroupOptions,
    PartInfo,
    PartSearchOption,
    PartSearchResult,
    PartTypeOptions,
    SavedAddress,
    SavedAddressesResult,
    SavedVehicle,
    SavedVehiclesResult,
    ShippingInfo,
    ToolCategories,
    ToolCategory,
    ToolInfo,
    ToolsResult,
    VehicleEngines,
    VehicleMakes,
    VehicleModels,
    VehiclePartCategories,
    VehiclePartsResult,
    VehicleYears,
    WhatIsPartCalledResult,
    WhatIsPartCalledResults,
)
from ..utils import PartExtractor
from .base import BaseClient

if TYPE_CHECKING:
    from .vehicle import Vehicle


class RockAutoClient(BaseClient):
    """
    Python client for RockAuto.com API interactions.

    Provides methods for searching vehicle parts with comprehensive filtering
    and Vehicle-scoped operations for intuitive part discovery.
    """

    def __init__(
        self,
        # === CAPTCHA BYPASS SETTINGS ===
        use_mobile_profile: bool = True,  # Mobile profile reduces CAPTCHA triggers
        # === CACHE SETTINGS ===
        enable_caching: bool = True,
        part_cache_hours: int = 12,
        search_cache_hours: int = 12,
        dropdown_cache_hours: int = 24,
        max_cached_parts: int = 1000,
        max_cached_searches: int = 100
    ):
        """
        Initialize client with configurable caching settings.

        Args:
            enable_caching: Enable/disable all caching (default: True)
            part_cache_hours: Hours to cache individual part data (default: 12)
            search_cache_hours: Hours to cache search results (default: 12)
            dropdown_cache_hours: Hours to cache dropdown options (default: 24)
            max_cached_parts: Maximum number of parts to cache (default: 1000)
            max_cached_searches: Maximum number of search results to cache (default: 100)
        """
        super().__init__(use_mobile_profile=use_mobile_profile)
        self._nck_token = None  # CAPTCHA bypass token
        self._session_initialized = False

        # === CACHE CONFIGURATION ===
        self.cache_config = CacheConfiguration(
            enabled=enable_caching,
            part_ttl_hours=part_cache_hours,
            result_ttl_hours=search_cache_hours,
            max_parts=max_cached_parts,
            max_results=max_cached_searches
        )

        # Initialize caches
        self._part_cache: Optional[PartCache] = self.cache_config.create_cache() if enable_caching else None

        # Dropdown caches (separate from main part cache for different TTL)
        self._dropdown_cache_hours = dropdown_cache_hours
        self._manufacturer_cache: Optional[ManufacturerOptions] = None
        self._part_group_cache: Optional[PartGroupOptions] = None
        self._part_type_cache: Optional[PartTypeOptions] = None

    async def _initialize_session(self):
        """Initialize session and extract _nck token for CAPTCHA bypass."""
        if self._session_initialized:
            return

        try:
            # Load the main page to get the _nck token
            response = await self.session.get("https://www.rockauto.com/")
            response.raise_for_status()

            # Extract _nck token from JavaScript
            html_content = response.text
            # Look for window._nck = "token"; pattern
            import re
            nck_match = re.search(r'window\._nck\s*=\s*"([^"]+)"', html_content)
            if nck_match:
                self._nck_token = nck_match.group(1)
            else:
                # Fallback: look for parent.window._nck pattern
                parent_match = re.search(r'parent\.window\._nck\s*=\s*"([^"]+)"', html_content)
                if parent_match:
                    self._nck_token = parent_match.group(1)

            self._session_initialized = True

        except Exception as e:
            # Session initialization failed, but continue without token
            # This will fall back to the old HTML scraping method
            self._session_initialized = True

    def _generate_jnck_token(self) -> str:
        """Generate _jnck parameter for API calls using the _nck token."""
        if not self._nck_token:
            return ""

        # URL encode the token for API usage
        encoded_token = urllib.parse.quote(self._nck_token, safe='')
        return f"&_jnck={encoded_token}"

    async def _call_catalog_api(self, function: str, payload: dict) -> dict:
        """
        Call the RockAuto catalog API using the same method as the browser.
        This bypasses CAPTCHA by using the proper AJAX headers and _jnck token.
        """
        await self._initialize_session()

        # Prepare the API call data exactly like the browser
        api_data = {
            "func": function,
            "payload": json.dumps(payload),
            "api_json_request": "1"
        }

        # Add CAPTCHA bypass token
        jnck_token = self._generate_jnck_token()
        if jnck_token:
            # Remove the leading & from _generate_jnck_token for form data
            api_data["_jnck"] = jnck_token[7:]  # Remove "&_jnck="

        # Use proper AJAX headers that match the browser
        headers = {
            "Accept": "text/plain, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.rockauto.com/",
            "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"iOS"',
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1",
        }

        try:
            response = await self.session.post(
                "https://www.rockauto.com/catalog/catalogapi.php",
                data=api_data,
                headers=headers
            )
            response.raise_for_status()

            # Parse JSON response
            return response.json()

        except Exception as e:
            raise Exception(f"Catalog API call failed: {str(e)}")


    # === PARTS SEARCH METHODS ===

    async def get_manufacturers(self, use_cache: bool = True) -> ManufacturerOptions:
        """
        Get all available manufacturers for parts search.

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            ManufacturerOptions containing all manufacturer options
        """
        if use_cache and self._manufacturer_cache:
            return self._manufacturer_cache

        try:
            response = await self.session.get("https://www.rockauto.com/en/partsearch/")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find manufacturer dropdown
            manufacturer_select = soup.find("select", {"id": "manufacturer_partsearch_007"})
            if not manufacturer_select:
                raise ValueError("Could not find manufacturer dropdown on parts search page")

            manufacturers = []
            for option in manufacturer_select.find_all("option"):
                value = option.get("value", "")
                text = option.get_text(strip=True)
                if text:  # Skip empty options
                    manufacturers.append(PartSearchOption(value=value, text=text))

            self._manufacturer_cache = ManufacturerOptions(
                manufacturers=manufacturers,
                count=len(manufacturers),
                last_updated=datetime.now().isoformat()
            )

            return self._manufacturer_cache

        except Exception as e:
            raise Exception(f"Failed to fetch manufacturers: {str(e)}")


    async def get_part_groups(self, use_cache: bool = True) -> PartGroupOptions:
        """
        Get all available part groups for parts search.

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            PartGroupOptions containing all part group options
        """
        if use_cache and self._part_group_cache:
            return self._part_group_cache

        try:
            response = await self.session.get("https://www.rockauto.com/en/partsearch/")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find part group dropdown
            part_group_select = soup.find("select", {"id": "partgroup_partsearch_007"})
            if not part_group_select:
                raise ValueError("Could not find part group dropdown on parts search page")

            part_groups = []
            for option in part_group_select.find_all("option"):
                value = option.get("value", "")
                text = option.get_text(strip=True)
                if text:  # Skip empty options
                    part_groups.append(PartSearchOption(value=value, text=text))

            self._part_group_cache = PartGroupOptions(
                part_groups=part_groups,
                count=len(part_groups),
                last_updated=datetime.now().isoformat()
            )

            return self._part_group_cache

        except Exception as e:
            raise Exception(f"Failed to fetch part groups: {str(e)}")


    async def get_part_types(self, use_cache: bool = True) -> PartTypeOptions:
        """
        Get all available part types for parts search.

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            PartTypeOptions containing all part type options
        """
        if use_cache and self._part_type_cache:
            return self._part_type_cache

        try:
            response = await self.session.get("https://www.rockauto.com/en/partsearch/")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find part type dropdown
            part_type_select = soup.find("select", {"id": "parttype_partsearch_007"})
            if not part_type_select:
                raise ValueError("Could not find part type dropdown on parts search page")

            part_types = []
            for option in part_type_select.find_all("option"):
                value = option.get("value", "")
                text = option.get_text(strip=True)
                if text:  # Skip empty options
                    part_types.append(PartSearchOption(value=value, text=text))

            self._part_type_cache = PartTypeOptions(
                part_types=part_types,
                count=len(part_types),
                last_updated=datetime.now().isoformat()
            )

            return self._part_type_cache

        except Exception as e:
            raise Exception(f"Failed to fetch part types: {str(e)}")


    async def search_parts_by_number(
        self,
        part_number: str,
        manufacturer: Optional[str] = None,
        part_group: Optional[str] = None,
        part_type: Optional[str] = None,
        part_name: Optional[str] = None
    ) -> PartSearchResult:
        """
        Search for parts by part number with optional filters.

        Args:
            part_number: Part number to search for (supports wildcards with *)
            manufacturer: Optional manufacturer filter (name or "All")
            part_group: Optional part group filter (name or "All")
            part_type: Optional part type filter (name or "All")
            part_name: Optional additional part name search text

        Returns:
            PartSearchResult containing found parts and search metadata
        """
        try:
            # Get initial page to extract security token
            response = await self.session.get("https://www.rockauto.com/en/partsearch/")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract security token
            nck_input = soup.find("input", {"name": "_nck"})
            if not nck_input:
                raise ValueError("Could not find security token on parts search page")

            security_token = nck_input.get("value", "")

            # Resolve filter values to their form values
            manufacturer_value = ""
            part_group_value = ""
            part_type_value = ""

            if manufacturer and manufacturer.lower() != "all":
                manufacturers = await self.get_manufacturers()
                mfr_option = manufacturers.get_manufacturer_by_name(manufacturer)
                if mfr_option:
                    manufacturer_value = mfr_option.value

            if part_group and part_group.lower() != "all":
                part_groups = await self.get_part_groups()
                group_option = part_groups.get_part_group_by_name(part_group)
                if group_option:
                    part_group_value = group_option.value

            if part_type and part_type.lower() != "all":
                part_types = await self.get_part_types()
                type_option = part_types.get_part_type_by_name(part_type)
                if type_option:
                    part_type_value = type_option.value

            # Prepare form data
            form_data = {
                "_nck": security_token,
                "dopartsearch": "1",
                "partsearch[partnum][partsearch_007]": part_number,
                "partsearch[manufacturer][partsearch_007]": manufacturer_value,
                "partsearch[partgroup][partsearch_007]": part_group_value,
                "partsearch[parttype][partsearch_007]": part_type_value,
                "partsearch[partname][partsearch_007]": part_name or "",
                "partsearch[do][partsearch_007]": "Search"
            }

            # Submit search
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.rockauto.com/en/partsearch/"
            }

            search_response = await self.session.post(
                "https://www.rockauto.com/en/partsearch/",
                data=form_data,
                headers=headers
            )
            search_response.raise_for_status()
            # Получаем оригинальный HTML
            original_html = search_response.text
            
            # Parse search results
            result_soup = BeautifulSoup(original_html, "lxml")
            with open('index.html', 'w') as f:
                f.write(original_html)

            parts = self._parse_parts_search_results(result_soup)

            return PartSearchResult(
                parts=parts,
                count=len(parts),
                search_term=part_number,
                manufacturer=manufacturer or "All",
                part_group=part_group or "All"
            )

        except Exception as e:
            raise Exception(f"Failed to search parts: {str(e)}")


    def _parse_parts_search_results(self, soup: BeautifulSoup) -> list[PartInfo]:
        """Parse parts from search results page."""
        parts = []

        result_tables = soup.find_all('div', id=re.compile(r'^listingcontainer\[\d+\]$'))

        for table in result_tables:
            part = self._extract_part_from_search_row(table)
            if part:
                parts.append(part)

        return parts


    def _extract_part_from_search_row(self, table) -> Optional[PartInfo]:
        """Extract part information from a search result row."""
        try:
            # Extract Link
            href = ""
            link = table.find("a", href=True, class_="ra-btn ra-btn-moreinfo")
            if link:
                href = link.get("href", "")
                if href and not href.startswith("http"):
                    href = f"https://www.rockauto.com{href}"
            
            # Extract name
            name = table.find('span', class_="span-link-underline-remover")
            if name:
                name = name.text

            # Extract brand
            brand = table.find('span', class_="listing-final-manufacturer no-text-select")
            if brand:
                brand = brand.text

            # Extract brand
            price = table.find('span', id=re.compile(r'^dprice\[\d+\]\[v\]$'))
            if price:
                price = price.text

            # Extract Part number
            part_number = table.find('span', class_="listing-final-partnumber no-text-select")
            if part_number:
                part_number = part_number.text

            # Extract IMG
            part_img = table.find('img', id=re.compile(r'^inlineimg_thumb\[\d+\]$'))
            if part_img:
                part_img = "https://www.rockauto.com"+part_img['src']

            return PartInfo(
                name=name.replace('Info', '').strip() if name else "Unknown",
                part_number=part_number,
                brand=brand.strip() if brand else 'Unknown',
                price=price.strip() if price else '0',
                url=href,
                specifications='{}',
                image_url=part_img
            )

        except Exception as e:
            print(e)
            return None

  

