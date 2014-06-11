require 'nokogiri'
require 'faraday'
require 'json'

# CONSTANTS
LAT_LONG_FILE = "./lat_long"


# X-Paths
PADMAPPER_PADLISTER_XPATH = "/html/body/div[@id='bar']/div[1]/div[@class='sideBarButtonDiv']/a[@class='normalButton whiteButton thumbButton sideBarNavButton'][2]/@href"
PADLISTER_XPATH = "/html/body[@id='listings_show']/div[@id='main_container']/div[@class='wrapper']/div[@id='body_div']/div[@id='left-col']/div[@id='summary']/ul/li"
PADLISTER_PRICE     = 1
PADLISTER_MIN_LEASE = 6
PADLISTER_ADDRESS   = 7

# REGEX
HTML_TAG_REGEX  = /(<[^>]*>)|\n|\t/s
PRICE_REGEX     = /(Price|\s)/
ADDRESS_REGEX   = /(Address)/
LEASE_REGEX     = /(Min\.\ Lease|\s)/

class Scraper

    def initialize
        @padmapper_url = "http://www.padmapper.com/"
        @padmapper_init_lat_long = "reloadMarkersJSON.php?eastLong=-121.81503295898438&northLat=37.951684787899445&westLong=-123.00155639648438&southLat=37.615496567899385&cities=false&showPOI=false&limit=999999&minRent=0&maxRent=6000&searchTerms=Words+Required+In+Listing&maxPricePerBedroom=6000&minBR=0&maxBR=10&minBA=1&maxAge=7&imagesOnly=false&phoneReq=false&cats=false&dogs=false&noFee=false&showSubs=true&showNonSubs=true&showRooms=true&showVac=true&userId=-1&cl=true&pl=true&aptsrch=true&rnt=true&airbnb=true&ood=true&af=true&rltr=true&zoom=12&favsOnly=false&onlyHQ=true&showHidden=false&am=false&workplaceLat=0&workplaceLong=0&maxTime=0"
        @padmapper_place_info = "show.php?id="

        @conn = Faraday.new(:url => @padmapper_url) do |faraday|
            faraday.adapter     Faraday.default_adapter
        end
    end

    def get_lat_longs
        resp = @conn.get(@padmapper_init_lat_long)
        JSON.parse(resp.body)
    end

    def get_place_info(id)
        resp = @conn.get(@padmapper_place_info + "#{id}")
        link = Nokogiri::HTML(resp.body).xpath(PADMAPPER_PADLISTER_XPATH).to_s
        resp = Faraday.get(link)

        html = Nokogiri::HTML(resp.body)
        listing_price = html.xpath(PADLISTER_XPATH + "[#{PADLISTER_PRICE}]").to_s
                                                                            .strip.gsub(HTML_TAG_REGEX,"")
                                                                            .gsub(PRICE_REGEX, "")
        listing_min_lease = html.xpath(PADLISTER_XPATH + "[#{PADLISTER_MIN_LEASE}]").to_s.strip
                                                                                    .gsub(HTML_TAG_REGEX, "")
                                                                                    .gsub(LEASE_REGEX, "")
        listing_address = html.xpath(PADLISTER_XPATH + "[#{PADLISTER_ADDRESS}]").to_s.strip
                                                                                .gsub(HTML_TAG_REGEX, "")
                                                                                .gsub(ADDRESS_REGEX, "")
                                                                                .strip
        "#{listing_price}, #{listing_min_lease}, #{listing_address.gsub(",","\\,")}"
    end
end

if __FILE__ == $0
    scraper = Scraper.new
    #lat_long = scraper.get_lat_longs # JSON of all the ID's of places
    temp_id = 187539045
    puts scraper.get_place_info temp_id
end