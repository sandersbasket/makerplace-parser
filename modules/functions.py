from re import I
import requests
from web3 import Web3
from settings import settings 
from modules import db

web3: Web3 = Web3(Web3.HTTPProvider(settings.config['infura_token']))
ether_price: int = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd').json()['ethereum']['usd']

database: db.Database = db.Database('./database.db')

def get_balance_address(address: str) -> float:
    check_sum: str = web3.toChecksumAddress(address)
    get_balance: int = web3.eth.get_balance(check_sum)
    get_balance_eth: float = web3.fromWei(get_balance, "ether")
    return round(get_balance_eth * int(ether_price))

def get_collections(page_size: int, start_index: int) -> list:
    headers: dict = {
        'authority': 'makersplace.com',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://makersplace.com',
        'pragma': 'no-cache',
        'referer': 'https://makersplace.com/marketplace/',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    json_data: dict = {
        'operationName': 'DigitalMediaSearch',
        'variables': {
            'pageSize': page_size,
            'startIndex': start_index,
        },
        'query': 'fragment ArtistFragment on ArtistType {\n  id\n  fullName\n  marketplaceUrl\n  profileImageUrl\n  landingUrl\n  fullLandingUrl\n  availableCreationCount\n  __typename\n}\n\nfragment ProductFragment on ProductType {\n  id\n  lowestAskInUsd\n  lowestAskInEth\n  lastSalePriceInUsd\n  lastSalePriceInEth\n  currentOwner {\n    id\n    fullName\n    marketplaceUrl\n    profileImageUrl\n    landingUrl\n    fullLandingUrl\n    __typename\n  }\n  hasReservePrice\n  reservePriceMet\n  printEdition\n  productUrl\n  auction {\n    id\n    endsAt\n    auctionEnded\n    __typename\n  }\n  sale {\n    id\n    custodialPriceInUsd\n    __typename\n  }\n  raffle {\n    id\n    startsAt\n    endsAt\n    __typename\n  }\n  liveBid {\n    id\n    bidAmount\n    isEtherBid\n    isCcBid\n    bidInEther\n    bidInUsd\n    __typename\n  }\n  hasUnlockable\n  __typename\n}\n\nfragment DigitalMediaFragment on DigitalMediaType {\n  id\n  mediaSlug\n  title\n  description\n  media1000xPreviewContent\n  media500xPreviewContent\n  hasVideo\n  videoUrl\n  totalSupply\n  collaborators {\n    ...ArtistFragment\n    __typename\n  }\n  metadata {\n    height\n    width\n    __typename\n  }\n  drop {\n    id\n    dropsAt\n    hasDropped\n    __typename\n  }\n  product {\n    ...ProductFragment\n    __typename\n  }\n  author {\n    ...ArtistFragment\n    __typename\n  }\n  collection {\n    id\n    collectionName\n    totalSupply\n    description\n    collectionLogoUrl\n    __typename\n  }\n  __typename\n}\n\nquery DigitalMediaSearch($format: [String!], $lowestAsk: [String], $price: [String!], $reserve: [String!], $offer: [String!], $status: [String!], $editions: [String!], $filter: [String!], $artist: [String!], $userStoreCollectionSlug: String, $owner: [String!], $pageSize: Int, $startIndex: Int, $sort: [String!], $mediaSlug: [String!], $collection: [String!], $collectionTraits: [String!], $collectionTraitsCount: [String!], $tags: [String!]) {\n  marketplace {\n    id\n    digitalMedia(\n      format: $format\n      lowestAsk: $lowestAsk\n      price: $price\n      reserve: $reserve\n      offer: $offer\n      status: $status\n      editions: $editions\n      filter: $filter\n      artist: $artist\n      userStoreCollectionSlug: $userStoreCollectionSlug\n      owner: $owner\n      pageSize: $pageSize\n      startIndex: $startIndex\n      sort: $sort\n      mediaSlug: $mediaSlug\n      collection: $collection\n      collectionTraits: $collectionTraits\n      collectionTraitsCount: $collectionTraitsCount\n      tags: $tags\n    ) {\n      id\n      hasNextPage\n      numUniqueOwners\n      totalResults\n      currentEthRateInUsd\n      collectionTraitCounts {\n        minTraitCount\n        maxTraitCount\n        __typename\n      }\n      collectionInsights {\n        name\n        value\n        unit\n        __typename\n      }\n      collection {\n        id\n        collectionName\n        totalSupply\n        description\n        collectionLogoUrl\n        collectionUrl\n        slug\n        author {\n          hidePublicStorefront\n          __typename\n        }\n        __typename\n      }\n      userStoreCollection {\n        id\n        storeName\n        displayLogoUrl\n        storeUrl\n        description\n        hidePublicStorefront\n        owner {\n          ...ArtistFragment\n          __typename\n        }\n        __typename\n      }\n      isCollectionView\n      isCollectorStore\n      isArtistStore\n      accountType\n      filters {\n        title\n        name\n        options {\n          label\n          value\n          count\n          __typename\n        }\n        isTrait\n        __typename\n      }\n      results {\n        ...DigitalMediaFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
    }

    response: requests.Response = requests.post('https://makersplace.com/graphql/', headers = headers, json = json_data).json()

    database.add_index_page(start_index)

    authors_info = [get_author_info(name['author']['landingUrl'].split('/')[1]) for name in response['data']['marketplace']['digitalMedia']['results']]
    return authors_info


def get_author_info(name: str) -> int: 
    headers: dict = {
        'authority': 'makersplace.com',
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': '',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://makersplace.com',
        'pragma': 'no-cache',
        'referer': 'https://makersplace.com/cgoldart/gallery/created/the-sacred-cyborg-collection',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    json_data: dict = {
        'query': 'query ProfilesQuery(\n  $slug: String!\n) {\n  profile(globalSlug: $slug) {\n    ...ProfilesFragment\n    id\n  }\n}\n\nfragment ProfilesFragment on ProfileType {\n  id\n  address\n  description\n  shortDescription\n  isCurrentUser\n  profileImageUrl\n  hasLikes\n  accountType\n  aboutBanner\n  dateJoined\n  displayName\n  fullName\n  hasCollectedDigitalMedias\n  slug\n  socialLinks {\n    id\n    linkType\n    value\n  }\n  curator {\n    id\n    username\n    fullName\n  }\n  defaultCategory {\n    id\n    categorySlug\n  }\n  defaultCollection {\n    id\n    categorySlug\n  }\n}\n',
        'variables': {
            'slug': name,
        },
    }

    response: requests.Response = requests.post('https://makersplace.com/graphql/', headers = headers, json = json_data).json()
    
    profile: list = response['data']['profile']
    address: str = profile.get('address')

    if address == None: 
        return print('Address not found, skip user')

    if database.is_address_exists(address): 
        return print('Skip address ->', address)

    address_balance: float = get_balance_address(address) if address else 0

    social_links: dict = profile.get('socialLinks', [])
    links: dict = {link['linkType']: link['value'] for link in social_links}
    
    print('Add address ->', address)
    return database.add_address(address, address_balance, links)