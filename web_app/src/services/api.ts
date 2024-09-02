import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosRequestConfig } from 'axios';

interface IResponse {
    result: boolean;
}

export interface IUser extends IResponse {
    id: number | null;
    chat_id: number | null;
    first_name: string | null;
    last_name: string | null;
    username: string | null;
    birthday: Date | null;
    photo_url: string | null;
    date_started: Date | null;
    share_link: string | null;
}

export interface IGetUser {
    id?: number, 
    chatID?: number, 
    username?: string,
    limit?: number, 
    offset?: number
}

export default class ApiService {
    private api: AxiosInstance;

    constructor(baseURL: string) {
        this.api = axios.create({
            baseURL: baseURL,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    get<T>(resource: string, params?: any): Promise<AxiosResponse<T>> {
        return this.api.get<T>(resource, {params: params});
    }

    post<T>(resource: string, data: any): Promise<AxiosResponse<T>> {
        return this.api.post<T>(resource, data);
    }

    put<T>(resource: string, data: any): Promise<AxiosResponse<T>> {
        return this.api.put<T>(resource, data);
    }

    delete<T>(resource: string): Promise<AxiosResponse<T>> {
        return this.api.delete<T>(resource);
    }

    validateInitData(initData: string): Promise<AxiosResponse<IUser>> {
        return this.post("/user/validate_init_data", {
            "init_data": initData
        })
    }

    setBirthday(userID: number, birthday: Date): Promise<AxiosResponse<IResponse>> {
        return this.post("/user/birthday", {
            "user_id": userID,
            "birthday": birthday
        })
    }

    getUser({id, chatID, username}: IGetUser): Promise<AxiosResponse<IUser | null>> {
        return this.get("/user", {
            "id": id,
            "chat_id": chatID,
            "username": username
        })
    }

    getUsers({limit, offset}: IGetUser): Promise<AxiosResponse<IUser[] | null>> {
        return this.get("/user", {"limit": limit, "offset": offset})
    }
}