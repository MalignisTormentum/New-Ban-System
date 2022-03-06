local HTTPS, DSS = game:GetService('HttpService'), game:GetService('DataStoreService')
local bans = DSS:GetDataStore('BanDataStore')
local link = "" -- Hiden for public display.

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
    local s, d = pcall(function()
        local discord_bans = Bans.get_all()
        for _, v in pairs(discord_bans) do
            if tonumber(v['days']) == 0 then
                wait(6)
                bans:RemoveAsync('Player_' .. v['user_id'])
                Bans.remove_ban(v['user_id'])
            end

            for _, p in pairs(game.Players:GetPlayers()) do
                if tonumber(v['user_id']) == p.UserId then
                    if os.time() > v['ban_date'] + v['days'] * 24 * 60 * 60 then
                        bans:RemoveAsync("Player_" .. p.UserId)
                    else
                        p:Kick("You were banned for " .. v['days'] .. ' days for reason: ' .. v['reason'])
                        bans:SetAsync('Player_' .. p.UserId, {os.time() + (tonumber(v['days']) * 24 * 60 * 60), v['reason']})
                    end
                    Bans.remove_ban(v['user_id'])
                end
            end
        end
    end)
    if not s then warn(d) end
    wait(120)
end