local HTTPS, DSS, MS = game:GetService('HttpService'), game:GetService('DataStoreService'), game:GetService('MessagingService')
local store = DSS:GetDataStore('BanDataStore')
local link, isNewestServer = "", true

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

game.Players.PlayerAdded:Connect(function(Player) -- Kick player when they join if they are banned.
	local success, data = pcall(function()  
		return store:GetAsync("Player_" .. Player.UserId)
	end)
	if success then
		if data then
			if os.time() > data[1] then
				store:RemoveAsync("Player_" .. Player.UserId)
				return
			end
			local Time = os.difftime(data[1], os.time())
			local Days = math.floor(Time/86400) .. " days, "
			local Hours = math.floor((Time%86400)/3600) .. " hours, "
			local Minutes = math.floor((Time%3600)/60) .. " minutes, and "
			local Seconds = math.floor(Time%60) .. " seconds"
			local RemainingTime = Days .. Hours .. Minutes .. Seconds
			Player:Kick("You're banned for another " .. RemainingTime .. " for " .. data[2] .. ".")
		end
	end
end)

local function SendMessage(d)
	pcall(function()
		MS:PublishAsync("Message", d)
	end)
end

pcall(function()
	MS:SubscribeAsync("Message", function(t)
		if not t.Data then
			isNewestServer = false
		else
			for _, Plr in pairs(game.Players:GetPlayers()) do
				if Plr.UserId == t.Data[1] then
					Plr:Kick("You were banned for " .. t.Data[2] .. " days for " .. t.Data[3])
					break
				end
			end
		end
	end)
end)

SendMessage(false) -- Have only the most current running game server handle requests to the database and inform the others. This keeps hits to the db low.

coroutine.wrap(function()
	while true do
		wait(300)
		if not isNewestServer then break end
		local s, d = pcall(function()
			local discord_bans = Bans.get_all()
			for _, v in pairs(discord_bans) do
				local user_id, days, reason = v['user_id'], tonumber(v['days']), v['reason']
				if days == 0 then
					store:RemoveAsync('Player_' .. user_id)
					Bans.remove_ban(user_id)
				elseif days > 0 then
					store:SetAsync('Player_' .. user_id, {os.time() + (days * 24 * 60 * 60), reason})
					Bans.remove_ban(user_id)
					for _, p in pairs(game.Players:GetPlayers()) do
						if tonumber(user_id) == p.UserId then
							p:Kick("You were banned for " .. days .. ' days for reason: ' .. reason)
						end
					end
					SendMessage({user_id, days, reason})
				end
			end
		end)
		if not s then warn(d) end
	end
end)()