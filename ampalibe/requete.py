import json
import mysql.connector

class Request:
    def __init__(self, conf):
        '''
            Init the database
            [conf] => {
                DB_HOST = ,
                DB_USER = ,
                DB_PASSWORD = ,
                DB_NAME = ,
                DB_PORT = 
            }

        '''
        self.DB_CONF = {
            'host': conf.DB_HOST,
            'user': conf.DB_USER,
            'password': conf.DB_PASSWORD,
            'database': conf.DB_NAME,
            'port': conf.DB_PORT
        }
        self.__connect()
        self.__init_db()

    def __connect(self):
        """
        The function which connect to the Database.
        """
        self.db = mysql.connector.connect(**self.DB_CONF)
        self.cursor = self.db.cursor()

    def __init_db(self):
        '''
            Creation des tables necessaires à l'applicatifs
        '''
        req = '''
            CREATE TABLE IF NOT EXISTS `amp_user` (
                `id` INT NOT NULL AUTO_INCREMENT,
                `user_id` varchar(50) NOT NULL UNIQUE,
                `action` varchar(50) DEFAULT NULL,
                `last_use` datetime NOT NULL DEFAULT current_timestamp(),
                `lang` varchar(5) DEFAULT NULL,
                `tmp` varchar(255) DEFAULT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        '''
        self.cursor.execute(req)
        self.db.commit()
    
    def verif_db(fonction):
        '''
            The function that checks if the database 
            is connected or not before doing an operation.
        '''
        def trt_verif(*arg, **kwarg):
            if not arg[0].db.is_connected():
                # reconnexion de la base
                try:
                    arg[0].db.reconnect()
                except Exception:
                    arg[0].__connect()
            return fonction(*arg, **kwarg)
        return trt_verif

    @verif_db
    def verif_user(self, user_id):
        '''
            Function to insert new user and/or update the date 
            of last use if the user already exists.

            Parameter :  user_id
            
        '''
        # Insertion dans la base si non present
        # Mise à jour du last_use si déja présent
        req = '''
            INSERT INTO amp_user(user_id) VALUES (%s)
            ON DUPLICATE KEY UPDATE last_use = NOW()
        '''
        self.cursor.execute(req, (user_id,))
        self.db.commit()
    
    @verif_db
    def get_action(self, user_id):
        '''
            Get action user

            Parameter :  user_id
        '''
        req = 'SELECT action FROM amp_user WHERE user_id = %s'
        self.cursor.execute(req, (user_id,))
        # retourne le resultat
        return self.cursor.fetchone()[0]
    
    @verif_db
    def set_action(self, user_id, action):
        '''
            Define aciton of an user 

            Parameter :  user_id
        '''
        req = 'UPDATE amp_user set action = %s WHERE user_id = %s'
        self.cursor.execute(req, (action, user_id))
        self.db.commit()
    
    @verif_db
    def __get_temp(self, user_id):
        '''
            Get temp parameter of an user

            Parameter :  user_id
        '''
        req = 'SELECT tmp FROM amp_user WHERE user_id = %s'
        self.cursor.execute(req, (user_id,))
        return self.cursor.fetchone()[0]

    @verif_db
    def set_temp(self, user_id, key, value):
        '''
            Insert or set a temp parameter of an user

            Parameter :  user_id
        '''
        data = self.__get_temp(user_id)
        if not data:
            data = {}
        else:
            data = json.loads(data)
        data[key] = value
        data = json.dumps(data)
        req = 'UPDATE amp_user SET tmp = %s WHERE user_id = %s'
        self.cursor.execute(req, (data, user_id))
        self.db.commit()

    @verif_db
    def get_temp(self, user_id, key):
        '''
            Get temp parameter of an user

            Parameter :  user_id ,key_temp
        '''
        data = self.__get_temp(user_id)
        if not data:
            return
        data = json.loads(data)
        return data.get(key)
    
    @verif_db
    def del_temp(self, user_id, key):
        '''
            Delete temp parameter of an user

            Parameter :  user_id ,key_temp
        '''
        data = self.__get_temp(user_id)
        if not data:
            return
        data = json.loads(data)
        try:
            data.pop(key)
        except KeyError:
            pass
        else:
            data = json.dumps(data)
            req = 'UPDATE amp_user SET tmp = %s WHERE user_id = %s'
            self.cursor.execute(req, (data, user_id))
            self.db.commit()
