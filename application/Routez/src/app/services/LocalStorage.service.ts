import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
})
export class LocalStorageService {
    /**
     * Adiciona um item ao localStorage.
     * @param key A chave usada como identificador.
     * @param value O valor a ser salvo, será convertido em JSON.
     */
    setItem<T>(key: string, value: T): void {
      try {
        const json = JSON.stringify(value);
        localStorage.setItem(key as string, json);
      } catch (error) {
        console.error('Erro ao salvar no localStorage:', error);
      }
    }
  
    /**
     * Recupera um item do localStorage e faz o parse para o tipo desejado.
     * @param key A chave do item.
     * @returns O valor convertido ou null se não encontrado ou inválido.
     */
    getItem<T>(key: string): T | null {
      try {
        const json = localStorage.getItem(key);
        if (!json) return null;
        return JSON.parse(json) as T;
      } catch (error) {
        console.error('Erro ao recuperar do localStorage:', error);
        return null;
      }
    }
  
    /**
     * Remove um item do localStorage pela chave.
     * @param key A chave a ser removida.
     */
    removeItem(key: string): void {
      localStorage.removeItem(key);
    }
  
    /**
     * Limpa todo o localStorage.
     */
    clear(): void {
      localStorage.clear();
    }
  }
  