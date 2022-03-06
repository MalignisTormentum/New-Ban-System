<?php
    class Connection{
        protected $pdo;
        public function __construct(PDO $pdo) {
            $this->pdo = $pdo;
        }
    }
    
    class Bans extends Connection {
        public function get_all($access_key){
            $query = $this->pdo->prepare('SELECT days, reason, user_id, ban_date
            FROM bans WHERE access_key=:access_key');
            $query->bindValue(':access_key', $access_key);
            $query->execute();
            $res = $query->fetchall();
            $query->closeCursor();
            return $res;
        }

        public function get_ban($access_key, $user_id){
            $query = $this->pdo->prepare('SELECT * FROM bans WHERE access_key=:access_key AND user_id=:user_id');
            $query->bindValue(':access_key', $access_key);
            $query->bindValue(':user_id', $user_id);
            $query->execute();
            $res = $query->fetch();
            $query->closeCursor();
            return $res;
        }

        public function set_ban($data){
            $query = $this->pdo->prepare('
                INSERT INTO bans
                    (access_key, user_id, ban_date, days, reason)
                VALUES
                    (:access_key, :user_id, :ban_date, :days, :reason)
                ');
    
            $query->bindValue(':access_key', $data['access_key']);
            $query->bindValue(':user_id', $data['user_id']);
            $query->bindValue(':ban_date', strtotime(date('Y-m-d H:i:s')));
            $query->bindValue(':days', $data['days']);
            $query->bindValue(':reason', $data['reason']);
            $query->execute();
            $query->closeCursor();
        }
        
        public function remove_ban($access_key, $user_id){
            $query = $this->pdo->prepare('DELETE FROM bans WHERE access_key=:access_key AND user_id=:user_id');
            $query->bindValue(':access_key', $access_key);
            $query->bindValue(':user_id', $user_id);
            $query->execute();
            $query->closeCursor();
        }
    }
    
    class Settings extends Connection {
        public function get_key($guild_id){
            $query = $this->pdo->prepare('SELECT * FROM guild_settings
            WHERE guild_id = :guild_id');
            $query->bindValue(':guild_id', $guild_id);
            $query->execute();
            $res = $query->fetchall();
            $query->closeCursor();
            return $res;
        }
        
        public function set_key($access_key, $guild_id){
            $query = $this->pdo->prepare('
                INSERT INTO guild_settings
                    (access_key, guild_id)
                VALUES
                    (:access_key, :guild_id)
                ');
    
            $query->bindValue(':access_key', $access_key);
            $query->bindValue(':guild_id', $guild_id);
            $query->execute();
            $query->closeCursor();
        }
        
        public function remove_key($guild_id){
            $query = $this->pdo->prepare('DELETE FROM guild_settings WHERE guild_id=:guild_id');
            $query->bindValue(':guild_id', $guild_id);
            $query->execute();
            $query->closeCursor();
        }
    }
        
    
    function is_valid($data){
        if(!array_key_exists('database', $data)){
            echo "MISSING 'database'";
            return false;
        }
        
        if(!array_key_exists('method', $data)){
            echo "MISSING 'method'";
            return false;
        }
        
        return true;
    }
    
    function filter_data($data){ 
        if (gettype($data['database']) == "string")
            return $data;
            
        return json_decode(array_keys($data)[0], true);
    }
    
    function fire_method($data){
        $db = new PDO( 
            // Args hidden for public display.
        );

        if (!is_valid($data))
            return "";
            
        if ($data['database'] == "bans"){
            $selected_db = new Bans($db);
            
            switch ($data['method']){
                case 'get_all':
                    return $selected_db->get_all($data['access_key']);
                case 'get_ban':
                    return $selected_db->get_ban($data['access_key'], $data['user_id']);
                case 'set_ban':
                    $selected_db->set_ban($data);
                    break;
                case 'remove_ban':
                    $selected_db->remove_ban($data['access_key'], $data['user_id']);
                    break;
                default:
                    echo "METHOD NOT FOUND ";
            }
        }
        
        if ($data['database'] == "guild_settings"){
            $selected_db = new Settings($db);
            
            switch ($data['method']){
                case 'get_key':
                    return $selected_db->get_key($data['guild_id']);
                case 'set_key':
                    $selected_db->set_key($data['access_key'], $data['guild_id']);
                    break;
                case 'remove_key':
                    $selected_db->remove_key($data['guild_id']);
                    break;
                default:
                    echo "METHOD NOT FOUND ";
            }
        }
    }

    if ($_SERVER['REQUEST_METHOD'] == "POST"){
        fire_method(filter_data($_POST));
    }
    
    if($_SERVER['REQUEST_METHOD'] == "GET"){
        echo json_encode(fire_method($_GET));
    }
?>