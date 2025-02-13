#%%
import os
from dotenv import load_dotenv

load_dotenv()

INFURA_API_KEY = os.getenv("INFURA_API_KEY")
DB_PATH = os.getenv("DB_PATH")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = os.getenv("ETHERSCAN_API_URL")


ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {   
        "constant": True,
        "inputs": [],
        "name": "owner",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    } 
    
]



cookies = {
    'night_mode': '2',
    'kdt': 'kHLTQ2qDup7srii8pE98aHLViKXqycWhhaeui37J',
    'g_state': '{"i_l":0}',
    'des_opt_in': 'Y',
    '_ga': 'GA1.2.665353668.1738650991',
    '_ga_RJGMY4G45L': 'GS1.2.1738650991.1.1.1738651225.16.0.0',
    'ph_phc_TXdpocbGVeZVm5VJmAsHTMrCofBQu3e0kN8HGMNGTVW_posthog': '%7B%22distinct_id%22%3A%220194cf9e-e238-7c5b-9941-673656d8d91a%22%2C%22%24sesid%22%3A%5B1738651715217%2C%220194cf9e-e236-7a11-b1e2-488bbbcd6576%22%2C1738650083894%5D%7D',
    'lang': 'en',
    'dnt': '1',
    'guest_id': 'v1%3A173882911237877291',
    'guest_id_marketing': 'v1%3A173882911237877291',
    'guest_id_ads': 'v1%3A173882911237877291',
    'gt': '1887412211930571180',
    'auth_token': '74702e1662ad0420ec7c7c3828f745814c9b0dbb',
    'ct0': 'c8cd7443f48ad0d6952f8ca0e2b9e6af524544128e61496851746bbaf36e508a37890ba1105e5c477cf31285eb2f2f5a0e0ac72e89706264bd9e537ea3cb41b66b34699bfa0c12d27a20eec9e4c3024f',
    'att': '1-RgNzk0x8Z6C5TQEiR2QX7hH8vW6liy8QTpqPEvzH',
    'twid': 'u%3D1840765474940088320',
    'personalization_id': '"v1_hsp7HogytO8VU7goCbASNQ=="',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'content-type': 'application/json',
    # 'cookie': 'night_mode=2; kdt=kHLTQ2qDup7srii8pE98aHLViKXqycWhhaeui37J; g_state={"i_l":0}; des_opt_in=Y; _ga=GA1.2.665353668.1738650991; _ga_RJGMY4G45L=GS1.2.1738650991.1.1.1738651225.16.0.0; ph_phc_TXdpocbGVeZVm5VJmAsHTMrCofBQu3e0kN8HGMNGTVW_posthog=%7B%22distinct_id%22%3A%220194cf9e-e238-7c5b-9941-673656d8d91a%22%2C%22%24sesid%22%3A%5B1738651715217%2C%220194cf9e-e236-7a11-b1e2-488bbbcd6576%22%2C1738650083894%5D%7D; lang=en; dnt=1; guest_id=v1%3A173882911237877291; guest_id_marketing=v1%3A173882911237877291; guest_id_ads=v1%3A173882911237877291; gt=1887412211930571180; auth_token=74702e1662ad0420ec7c7c3828f745814c9b0dbb; ct0=c8cd7443f48ad0d6952f8ca0e2b9e6af524544128e61496851746bbaf36e508a37890ba1105e5c477cf31285eb2f2f5a0e0ac72e89706264bd9e537ea3cb41b66b34699bfa0c12d27a20eec9e4c3024f; att=1-RgNzk0x8Z6C5TQEiR2QX7hH8vW6liy8QTpqPEvzH; twid=u%3D1840765474940088320; personalization_id="v1_hsp7HogytO8VU7goCbASNQ=="',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-client-transaction-id': '4Pfd3N0wclKtsIeEv5nP3TUWC+7lpcq02dtixwqTjtDkki8/LkZapei4OcUbuXDilevqteNOVH+BH0llaHyRtV20l5FX4w',
    'x-client-uuid': '7ea905c5-65e0-4004-9c55-276ccf5549ac',
    'x-csrf-token': 'c8cd7443f48ad0d6952f8ca0e2b9e6af524544128e61496851746bbaf36e508a37890ba1105e5c477cf31285eb2f2f5a0e0ac72e89706264bd9e537ea3cb41b66b34699bfa0c12d27a20eec9e4c3024f',
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'x-twitter-client-language': 'en',
}

get_tweet_features =  '{"profile_label_improvements_pcf_label_in_post_enabled":true,"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"premium_content_api_read_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"responsive_web_grok_analyze_button_fetch_trends_enabled":false,"responsive_web_grok_analyze_post_followups_enabled":true,"responsive_web_jetfuel_frame":false,"responsive_web_grok_share_attachment_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"responsive_web_grok_analysis_button_from_backend":true,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_grok_image_annotation_enabled":true,"responsive_web_enhance_cards_enabled":false}'
get_user_features = '{"hidden_profile_subscriptions_enabled":true,"profile_label_improvements_pcf_label_in_post_enabled":true,"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_is_identity_verified_enabled":true,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"responsive_web_twitter_article_notes_tab_enabled":true,"subscriptions_feature_can_gift_premium":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}'
tweet_fieldToggles = '{"withArticlePlainText":false}'
user_fieldToggles = '{"withAuxiliaryUserLabels":false}'

get_tweet_url = 'https://x.com/i/api/graphql/Y9WM4Id6UcGFE8Z-hbnixw/UserTweets'
get_user_url = 'https://x.com/i/api/graphql/32pL5BWe9WKeSK1MoPvFQQ/UserByScreenName' 

