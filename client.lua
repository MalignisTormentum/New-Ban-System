local HTTPS, DSS = game:GetService('HttpService'), game:GetService('DataStoreService')
local ban_store = DSS:GetDataStore('BanDataStore')
local link = "https://www.malignistormentum.site/database_connection.php"

local access_key = "" -- ADD ACCESS KEY HERE.

if access_key == "" then
    error("Your access key must be set and it must be the same as the one used on Discord.")
end

local Bans = {}
Bans.__index = Bans

function Bans.get_all()
    return HTTPS:JSONDecode(HTTPS:GetAsync(link .. "?database=bans&method=get_all&access_key=" .. access_key))
end

function Bans.remove_ban(user_id)
    local data = {
        ['method'] = 'remove_ban',
        ['access_key'] = access_key,
        ['database'] = 'bans',
        ['user_id'] = user_id
    }
    HTTPS:PostAsync(link, HTTPS:JSONEncode(data), Enum.HttpContentType.ApplicationUrlEncoded)
end

while true do
    wait(300)
    local s, d = pcall(function()
        local discord_bans, banned_players = Bans.get_all(), {}
        for _, v in pairs(discord_bans) do
            wait(6)
            if tonumber(v['days']) == 0 then
                ban_store:RemoveAsync('Player_' .. v['user_id'])
                Bans.remove_ban(v['user_id'])
            elseif tonumber(v['days']) > 0 then
                ban_store:SetAsync('Player_' .. v['user_id'], {os.time() + (tonumber(v['days']) * 24 * 60 * 60), v['reason']})
                Bans.remove_ban(v['user_id'])
                table.insert(banned_players, v)
            end
        end
        for _, v in pairs(banned_players) do
            for _, p in pairs(game.Players:GetPlayers()) do
                if tonumber(v['user_id']) == p.UserId then
                    p:Kick("You were banned for " .. v['days'] .. ' days for reason: ' .. v['reason'])
                end
            end
        end
    end)
    if not s then warn(d) end
end